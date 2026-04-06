"""Ajustement des prévisions selon le scénario."""

from app.config import SCENARIO_ADJUSTMENTS


class ScenarioAdjuster:
    """Fournit les paramètres d'ajustement pour chaque scénario."""

    @staticmethod
    def get_params(scenario: str) -> dict:
        """Retourne les paramètres d'ajustement pour un scénario donné.

        - retard_client_jours : jours de retard/avance sur les encaissements clients
        - taux_conversion_commandes : ajustement du taux de conversion des commandes
        - avance_fournisseur_jours : jours de décalage sur les décaissements fournisseurs
        """
        return SCENARIO_ADJUSTMENTS.get(scenario, SCENARIO_ADJUSTMENTS["central"])

    @staticmethod
    def adjust_confidence(base_confidence: float, scenario: str) -> float:
        """Ajuste le taux de confiance de conversion selon le scénario."""
        params = SCENARIO_ADJUSTMENTS.get(scenario, SCENARIO_ADJUSTMENTS["central"])
        adjusted = base_confidence + params["taux_conversion_commandes"]
        return max(0.0, min(1.0, adjusted))
