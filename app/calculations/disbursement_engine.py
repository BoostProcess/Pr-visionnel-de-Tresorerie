"""Moteur de calcul des décaissements."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.calculations.due_date_calculator import DueDateCalculator
from app.calculations.order_converter import OrderConverter
from app.models.cash import LignePrevisionnel
from app.models.invoices import Avoir, FactureFournisseur
from app.models.orders import CommandeFournisseur


class DisbursementEngine:
    """Calcule les décaissements prévisionnels."""

    def __init__(self):
        self._due_date_calc = DueDateCalculator()
        self._order_converter = OrderConverter()

    def compute_disbursements(
        self,
        session: Session,
        scenario: str,
        start_month: date,
        months: int,
        late_days: int = 0,
        conversion_delay: int = 30,
        confidence_pct: float = 0.95,
    ) -> list[LignePrevisionnel]:
        """Calcule tous les décaissements pour la période."""
        end_month = date(
            start_month.year + (start_month.month + months - 1) // 12,
            (start_month.month + months - 1) % 12 + 1,
            1,
        )

        lines = []
        lines.extend(
            self._process_open_invoices(session, scenario, start_month, end_month, late_days)
        )
        lines.extend(
            self._process_supplier_orders(
                session, scenario, start_month, end_month,
                late_days, conversion_delay, confidence_pct,
            )
        )
        lines.extend(
            self._apply_supplier_credit_notes(session, scenario, start_month, end_month)
        )
        return lines

    def _process_open_invoices(
        self, session: Session, scenario: str,
        start: date, end: date, late_days: int,
    ) -> list[LignePrevisionnel]:
        """Traite les factures fournisseurs ouvertes."""
        lines = []
        invoices = (
            session.query(FactureFournisseur)
            .filter(FactureFournisseur.statut.in_(["ouvert", "partiel"]))
            .filter(FactureFournisseur.reste_a_regler > 0)
            .all()
        )

        for inv in invoices:
            montant = inv.reste_a_regler

            # Calcul date d'échéance
            if inv.date_echeance:
                due_date = inv.date_echeance
            elif inv.fournisseur and inv.fournisseur.condition_reglement:
                due_date = self._due_date_calc.calculate(
                    inv.date_facture, inv.fournisseur.condition_reglement
                )
            else:
                due_date = inv.date_facture + timedelta(days=30)

            # Ajustement scénario (fournisseurs : délai inversé)
            due_date = self._due_date_calc.calculate_with_scenario(due_date, -late_days)
            mois = due_date.replace(day=1)

            if mois < start or mois >= end:
                continue

            lines.append(
                LignePrevisionnel(
                    scenario=scenario,
                    mois=mois,
                    categorie="decaissement_facture",
                    sous_categorie="facture_fournisseur",
                    source_type="facture_fournisseur",
                    source_id=inv.id,
                    nom_tiers=inv.fournisseur.name if inv.fournisseur else None,
                    montant=-montant,  # Négatif = décaissement
                    date_echeance=due_date,
                )
            )
        return lines

    def _process_supplier_orders(
        self, session: Session, scenario: str,
        start: date, end: date,
        late_days: int, conversion_delay: int, confidence_pct: float,
    ) -> list[LignePrevisionnel]:
        """Traite les commandes fournisseurs non facturées."""
        lines = []
        orders = (
            session.query(CommandeFournisseur)
            .filter(CommandeFournisseur.statut.in_(["ouverte", "partielle"]))
            .filter(CommandeFournisseur.reste_a_facturer > 0)
            .all()
        )

        for order in orders:
            payment_term = None
            if order.fournisseur and order.fournisseur.condition_reglement:
                payment_term = order.fournisseur.condition_reglement

            line = self._order_converter.project_supplier_order(
                order=order,
                payment_term=payment_term,
                conversion_delay_days=conversion_delay,
                confidence_pct=confidence_pct,
                late_days=-late_days,
                scenario=scenario,
            )
            if line and start <= line.mois < end:
                lines.append(line)

        return lines

    def _apply_supplier_credit_notes(
        self, session: Session, scenario: str, start: date, end: date,
    ) -> list[LignePrevisionnel]:
        """Les avoirs fournisseurs réduisent les décaissements."""
        lines = []
        avoirs = (
            session.query(Avoir)
            .filter(Avoir.type_tiers == "fournisseur")
            .filter(Avoir.est_impute == False)
            .all()
        )

        for avoir in avoirs:
            mois = avoir.date_avoir.replace(day=1)
            if mois < start or mois >= end:
                continue

            lines.append(
                LignePrevisionnel(
                    scenario=scenario,
                    mois=mois,
                    categorie="avoir_fournisseur",
                    sous_categorie="avoir",
                    source_type="avoir",
                    source_id=avoir.id,
                    montant=avoir.montant_ttc,  # Positif = réduit les décaissements
                    date_echeance=avoir.date_avoir,
                )
            )
        return lines
