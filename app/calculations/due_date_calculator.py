"""Calcul des dates d'échéance à partir des conditions de règlement."""

import calendar
from datetime import date, timedelta

from app.models.reference import ConditionReglement


class DueDateCalculator:
    """Calcule la date réelle d'encaissement/décaissement."""

    def calculate(self, invoice_date: date, payment_term: ConditionReglement) -> date:
        """Calcule la date d'échéance à partir de la date de facture et de la condition.

        Exemples :
        - "30 jours net" : date_facture + 30 jours
        - "30 jours fin de mois" : date_facture + 30 -> dernier jour du mois
        - "45 jours fin de mois le 10" : date_facture + 45 -> fin de mois -> 10 du mois suivant
        - "60 jours net" : date_facture + 60 jours
        """
        # Étape 1 : ajouter les jours de base
        intermediate = invoice_date + timedelta(days=payment_term.base_jours)

        # Étape 2 : si fin de mois, aller au dernier jour du mois
        if payment_term.fin_de_mois:
            last_day = calendar.monthrange(intermediate.year, intermediate.month)[1]
            intermediate = intermediate.replace(day=last_day)

        # Étape 3 : si jour du mois défini, aller à ce jour du mois suivant
        if payment_term.jour_du_mois is not None and payment_term.jour_du_mois > 0:
            # Passer au mois suivant
            if intermediate.month == 12:
                next_month = 1
                next_year = intermediate.year + 1
            else:
                next_month = intermediate.month + 1
                next_year = intermediate.year

            # Limiter au nombre de jours du mois
            max_day = calendar.monthrange(next_year, next_month)[1]
            day = min(payment_term.jour_du_mois, max_day)
            intermediate = date(next_year, next_month, day)

        return intermediate

    def calculate_with_scenario(
        self, base_due_date: date, late_days: int
    ) -> date:
        """Ajuste la date d'échéance selon le scénario (retard/avance)."""
        return base_due_date + timedelta(days=late_days)
