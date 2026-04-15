"""Moteur principal du prévisionnel de trésorerie."""

from datetime import date

from sqlalchemy.orm import Session

from app.calculations.collection_engine import CollectionEngine
from app.calculations.disbursement_engine import DisbursementEngine
from app.calculations.fixed_charge_engine import FixedChargeEngine
from app.calculations.monthly_aggregator import MonthSummary, MonthlyAggregator
from app.calculations.scenario_adjuster import ScenarioAdjuster
from app.calculations.vat_engine import VATEngine
from app.models.adjustments import AjustementManuel
from app.models.cash import LignePrevisionnel, PositionTresorerie
from app.models.assumptions import HypotheseConversion
from app.models.versions import VersionMensuelle
from app.config import FORECAST_MONTHS, SCENARIOS


class ForecastEngine:
    """Orchestre le calcul complet du prévisionnel sur tous les scénarios."""

    def __init__(self, session: Session):
        self.session = session
        self._collection_engine = CollectionEngine()
        self._disbursement_engine = DisbursementEngine()
        self._fixed_charge_engine = FixedChargeEngine()
        self._vat_engine = VATEngine()
        self._aggregator = MonthlyAggregator()

    def run_forecast(
        self,
        start_month: date | None = None,
        months: int = FORECAST_MONTHS,
    ) -> dict[str, list[MonthSummary]]:
        """Lance le prévisionnel complet pour les 3 scénarios.

        Returns:
            {"prudent": [MonthSummary, ...], "central": [...], "ambitieux": [...]}
        """
        if start_month is None:
            today = date.today()
            start_month = today.replace(day=1)

        initial_cash = self._get_initial_cash()

        # Charger les hypothèses de conversion
        conversion = (
            self.session.query(HypotheseConversion)
            .filter(HypotheseConversion.type_commande == "client")
            .first()
        )
        base_delay = conversion.delai_moyen_facturation if conversion else 30
        base_confidence = float(conversion.taux_confiance) / 100.0 if conversion else 0.90

        results = {}

        for scenario in SCENARIOS:
            params = ScenarioAdjuster.get_params(scenario)
            late_days = params["retard_client_jours"]
            supplier_advance = params["avance_fournisseur_jours"]
            confidence = ScenarioAdjuster.adjust_confidence(base_confidence, scenario)

            all_lines: list[LignePrevisionnel] = []

            # 1. Encaissements (factures + commandes clients)
            collections = self._collection_engine.compute_collections(
                session=self.session,
                scenario=scenario,
                start_month=start_month,
                months=months,
                late_days=late_days,
                conversion_delay=base_delay,
                confidence_pct=confidence,
            )
            all_lines.extend(collections)

            # 2. Décaissements (factures + commandes fournisseurs)
            disbursements = self._disbursement_engine.compute_disbursements(
                session=self.session,
                scenario=scenario,
                start_month=start_month,
                months=months,
                late_days=supplier_advance,
                conversion_delay=base_delay,
                confidence_pct=0.95,
            )
            all_lines.extend(disbursements)

            # 3. Charges fixes
            fixed = self._fixed_charge_engine.project_fixed_charges(
                self.session, scenario, start_month, months,
            )
            all_lines.extend(fixed)

            # 4. Emprunts
            loans = self._fixed_charge_engine.project_loans(
                self.session, scenario, start_month, months,
            )
            all_lines.extend(loans)

            # 5. Taxes à montant fixe
            taxes = self._fixed_charge_engine.project_taxes(
                self.session, scenario, start_month, months,
            )
            all_lines.extend(taxes)

            # 6. Ajustements manuels
            manual = self._load_manual_adjustments(scenario, start_month, months)
            all_lines.extend(manual)

            # 7. TVA
            vat = self._vat_engine.compute_vat_payments(
                all_lines, scenario, start_month, months,
            )
            all_lines.extend(vat)

            # 8. Stocker en base
            self._store_lines(all_lines, scenario)

            # 9. Agréger par mois
            summaries = self._aggregator.aggregate(all_lines, initial_cash)
            results[scenario] = summaries

        return results

    def recalculate(self):
        """Supprime les lignes non verrouillées et relance le calcul."""
        # Identifier les mois verrouillés
        locked_months = {
            v.mois
            for v in self.session.query(VersionMensuelle)
            .filter(VersionMensuelle.est_verrouille == True)
            .all()
        }

        # Supprimer les lignes non verrouillées
        existing = self.session.query(LignePrevisionnel).all()
        for line in existing:
            if line.mois not in locked_months:
                self.session.delete(line)
        self.session.flush()

        return self.run_forecast()

    def _get_initial_cash(self) -> int:
        """Récupère la trésorerie initiale."""
        position = (
            self.session.query(PositionTresorerie)
            .filter(PositionTresorerie.est_initial == True)
            .order_by(PositionTresorerie.date.desc())
            .first()
        )
        return position.solde_banque if position else 0

    def _load_manual_adjustments(
        self, scenario: str, start_month: date, months: int,
    ) -> list[LignePrevisionnel]:
        """Charge les ajustements manuels comme lignes de prévisionnel."""
        end_month = self._add_months(start_month, months)
        adjustments = (
            self.session.query(AjustementManuel)
            .filter(AjustementManuel.mois >= start_month)
            .filter(AjustementManuel.mois < end_month)
            .all()
        )
        lines = []
        for adj in adjustments:
            montant = adj.montant if adj.direction == "encaissement" else -adj.montant
            lines.append(
                LignePrevisionnel(
                    scenario=scenario,
                    mois=adj.mois,
                    categorie="ajustement_manuel",
                    sous_categorie=adj.categorie,
                    source_type="ajustement_manuel",
                    source_id=adj.id,
                    nom_tiers=adj.libelle,
                    montant=montant,
                    date_echeance=adj.mois,
                    notes=adj.notes,
                )
            )
        return lines

    def _store_lines(self, lines: list[LignePrevisionnel], scenario: str):
        """Stocke les lignes en base (remplace les existantes pour ce scénario)."""
        # Supprimer les anciennes lignes pour ce scénario (non verrouillées)
        locked_months = {
            v.mois
            for v in self.session.query(VersionMensuelle)
            .filter(VersionMensuelle.est_verrouille == True)
            .all()
        }

        old_lines = (
            self.session.query(LignePrevisionnel)
            .filter(LignePrevisionnel.scenario == scenario)
            .all()
        )
        for old in old_lines:
            if old.mois not in locked_months:
                self.session.delete(old)
        self.session.flush()

        # Ajouter les nouvelles lignes (hors mois verrouillés)
        for line in lines:
            if line.mois not in locked_months:
                self.session.add(line)
        self.session.flush()

    @staticmethod
    def _add_months(start: date, months: int) -> date:
        month = start.month + months
        year = start.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        return date(year, month, 1)
