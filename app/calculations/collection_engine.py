"""Moteur de calcul des encaissements."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.calculations.due_date_calculator import DueDateCalculator
from app.calculations.order_converter import OrderConverter
from app.models.cash import LignePrevisionnel
from app.models.invoices import Avoir, FactureClient
from app.models.orders import CommandeClient
from app.models.reference import Client


class CollectionEngine:
    """Calcule les encaissements prévisionnels."""

    def __init__(self):
        self._due_date_calc = DueDateCalculator()
        self._order_converter = OrderConverter()

    def compute_collections(
        self,
        session: Session,
        scenario: str,
        start_month: date,
        months: int,
        late_days: int = 0,
        conversion_delay: int = 30,
        confidence_pct: float = 0.90,
    ) -> list[LignePrevisionnel]:
        """Calcule tous les encaissements pour la période."""
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
            self._process_client_orders(
                session, scenario, start_month, end_month,
                late_days, conversion_delay, confidence_pct,
            )
        )
        lines.extend(
            self._apply_client_credit_notes(session, scenario, start_month, end_month)
        )
        return lines

    def _process_open_invoices(
        self, session: Session, scenario: str,
        start: date, end: date, late_days: int,
    ) -> list[LignePrevisionnel]:
        """Traite les factures clients ouvertes."""
        lines = []
        invoices = (
            session.query(FactureClient)
            .filter(FactureClient.statut.in_(["ouvert", "partiel"]))
            .filter(FactureClient.reste_a_regler > 0)
            .all()
        )

        for inv in invoices:
            # Gestion des litiges selon scénario
            if inv.en_litige:
                if scenario == "prudent":
                    continue
                elif scenario == "central":
                    montant = inv.reste_a_regler // 2
                else:
                    montant = inv.reste_a_regler
            else:
                montant = inv.reste_a_regler

            if montant <= 0:
                continue

            # Calcul date d'échéance
            if inv.date_echeance:
                due_date = inv.date_echeance
            elif inv.client and inv.client.condition_reglement:
                due_date = self._due_date_calc.calculate(
                    inv.date_facture, inv.client.condition_reglement
                )
            else:
                due_date = inv.date_facture + timedelta(days=30)

            # Ajustement scénario
            due_date = self._due_date_calc.calculate_with_scenario(due_date, late_days)
            mois = due_date.replace(day=1)

            # Ne garder que si dans la période
            if mois < start or mois >= end:
                continue

            lines.append(
                LignePrevisionnel(
                    scenario=scenario,
                    mois=mois,
                    categorie="encaissement_facture",
                    sous_categorie="facture_client",
                    source_type="facture_client",
                    source_id=inv.id,
                    nom_tiers=inv.client.name if inv.client else None,
                    montant=montant,
                    date_echeance=due_date,
                )
            )
        return lines

    def _process_client_orders(
        self, session: Session, scenario: str,
        start: date, end: date,
        late_days: int, conversion_delay: int, confidence_pct: float,
    ) -> list[LignePrevisionnel]:
        """Traite les commandes clients non facturées."""
        lines = []
        orders = (
            session.query(CommandeClient)
            .filter(CommandeClient.statut.in_(["ouverte", "partielle"]))
            .filter(CommandeClient.reste_a_facturer > 0)
            .all()
        )

        for order in orders:
            payment_term = None
            if order.client and order.client.condition_reglement:
                payment_term = order.client.condition_reglement

            line = self._order_converter.project_client_order(
                order=order,
                payment_term=payment_term,
                conversion_delay_days=conversion_delay,
                confidence_pct=confidence_pct,
                late_days=late_days,
                scenario=scenario,
            )
            if line and start <= line.mois < end:
                lines.append(line)

        return lines

    def _apply_client_credit_notes(
        self, session: Session, scenario: str, start: date, end: date,
    ) -> list[LignePrevisionnel]:
        """Les avoirs clients réduisent les encaissements."""
        lines = []
        avoirs = (
            session.query(Avoir)
            .filter(Avoir.type_tiers == "client")
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
                    categorie="avoir_client",
                    sous_categorie="avoir",
                    source_type="avoir",
                    source_id=avoir.id,
                    montant=-avoir.montant_ttc,  # Négatif = réduit les encaissements
                    date_echeance=avoir.date_avoir,
                )
            )
        return lines
