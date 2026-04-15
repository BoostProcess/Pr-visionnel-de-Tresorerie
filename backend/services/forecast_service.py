"""Service façade pour le prévisionnel, utilisé par l'UI."""

from datetime import date

from sqlalchemy.orm import Session

from app.calculations.forecast_engine import ForecastEngine
from app.calculations.monthly_aggregator import MonthSummary
from app.models.cash import LignePrevisionnel
from app.config import SCENARIOS


class ForecastService:
    """Interface simplifiée pour l'UI Streamlit."""

    def __init__(self, session: Session):
        self.session = session
        self._engine = ForecastEngine(session)

    def run_forecast(
        self, start_month: date | None = None, months: int = 24,
    ) -> dict[str, list[MonthSummary]]:
        """Lance le calcul complet."""
        return self._engine.run_forecast(start_month, months)

    def recalculate(self) -> dict[str, list[MonthSummary]]:
        """Recalcule le prévisionnel."""
        return self._engine.recalculate()

    def get_forecast_lines(
        self, scenario: str, mois: date | None = None,
        categorie: str | None = None,
    ) -> list[LignePrevisionnel]:
        """Récupère les lignes de prévisionnel filtrées."""
        query = self.session.query(LignePrevisionnel).filter(
            LignePrevisionnel.scenario == scenario
        )
        if mois:
            query = query.filter(LignePrevisionnel.mois == mois)
        if categorie:
            query = query.filter(LignePrevisionnel.categorie == categorie)
        return query.order_by(LignePrevisionnel.date_echeance).all()

    def get_encaissements(
        self, scenario: str, mois: date | None = None,
    ) -> list[LignePrevisionnel]:
        """Récupère les lignes d'encaissement."""
        query = (
            self.session.query(LignePrevisionnel)
            .filter(LignePrevisionnel.scenario == scenario)
            .filter(LignePrevisionnel.montant > 0)
        )
        if mois:
            query = query.filter(LignePrevisionnel.mois == mois)
        return query.order_by(LignePrevisionnel.mois, LignePrevisionnel.date_echeance).all()

    def get_decaissements(
        self, scenario: str, mois: date | None = None,
    ) -> list[LignePrevisionnel]:
        """Récupère les lignes de décaissement."""
        query = (
            self.session.query(LignePrevisionnel)
            .filter(LignePrevisionnel.scenario == scenario)
            .filter(LignePrevisionnel.montant < 0)
        )
        if mois:
            query = query.filter(LignePrevisionnel.mois == mois)
        return query.order_by(LignePrevisionnel.mois, LignePrevisionnel.date_echeance).all()

    def has_forecast_data(self) -> bool:
        """Vérifie s'il y a des données de prévisionnel."""
        return self.session.query(LignePrevisionnel).first() is not None
