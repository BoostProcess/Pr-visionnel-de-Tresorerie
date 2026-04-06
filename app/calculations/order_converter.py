"""Conversion des commandes en flux de trésorerie prévisionnels."""

from datetime import date, timedelta

from app.calculations.due_date_calculator import DueDateCalculator
from app.models.cash import LignePrevisionnel
from app.models.reference import ConditionReglement


class OrderConverter:
    """Projette quand une commande se transforme en encaissement/décaissement."""

    def __init__(self):
        self._due_date_calc = DueDateCalculator()

    def project_client_order(
        self,
        order,
        payment_term: ConditionReglement | None,
        conversion_delay_days: int = 30,
        confidence_pct: float = 0.90,
        late_days: int = 0,
        scenario: str = "central",
    ) -> LignePrevisionnel | None:
        """Convertit une commande client en ligne de prévisionnel.

        1. Déterminer date de facturation prévue
        2. Appliquer taux de confiance sur le montant
        3. Calculer date d'encaissement via condition de règlement
        4. Ajuster selon scénario
        """
        if order.reste_a_facturer <= 0:
            return None

        # Date de facturation prévue
        billing_date = order.date_facturation_prevue
        if billing_date is None:
            billing_date = order.date_commande + timedelta(days=conversion_delay_days)

        # Montant avec taux de confiance
        montant = int(order.reste_a_facturer * confidence_pct)
        if montant <= 0:
            return None

        # Date d'encaissement
        if payment_term:
            due_date = self._due_date_calc.calculate(billing_date, payment_term)
        else:
            due_date = billing_date + timedelta(days=30)

        # Ajustement scénario
        due_date = self._due_date_calc.calculate_with_scenario(due_date, late_days)

        # Mois de rattachement (1er du mois)
        mois = due_date.replace(day=1)

        return LignePrevisionnel(
            scenario=scenario,
            mois=mois,
            categorie="encaissement_commande",
            sous_categorie="commande_client",
            source_type="commande_client",
            source_id=order.id,
            nom_tiers=getattr(order, "client", None) and order.client.name,
            montant=montant,
            date_echeance=due_date,
        )

    def project_supplier_order(
        self,
        order,
        payment_term: ConditionReglement | None,
        conversion_delay_days: int = 30,
        confidence_pct: float = 0.95,
        late_days: int = 0,
        scenario: str = "central",
    ) -> LignePrevisionnel | None:
        """Convertit une commande fournisseur en ligne de prévisionnel (décaissement)."""
        if order.reste_a_facturer <= 0:
            return None

        billing_date = order.date_facturation_prevue
        if billing_date is None:
            billing_date = order.date_commande + timedelta(days=conversion_delay_days)

        montant = int(order.reste_a_facturer * confidence_pct)
        if montant <= 0:
            return None

        if payment_term:
            due_date = self._due_date_calc.calculate(billing_date, payment_term)
        else:
            due_date = billing_date + timedelta(days=30)

        due_date = self._due_date_calc.calculate_with_scenario(due_date, late_days)
        mois = due_date.replace(day=1)

        return LignePrevisionnel(
            scenario=scenario,
            mois=mois,
            categorie="decaissement_commande",
            sous_categorie="commande_fournisseur",
            source_type="commande_fournisseur",
            source_id=order.id,
            nom_tiers=getattr(order, "fournisseur", None) and order.fournisseur.name,
            montant=-montant,  # Négatif = décaissement
            date_echeance=due_date,
        )
