"""Tests du calculateur de dates d'échéance."""

from datetime import date

import pytest

from app.calculations.due_date_calculator import DueDateCalculator
from app.models.reference import ConditionReglement


class TestDueDateCalculator:
    """Tests des différentes conditions de règlement."""

    def setup_method(self):
        self.calc = DueDateCalculator()

    def _make_term(self, base_jours, fin_de_mois=False, jour_du_mois=None):
        """Helper pour créer une condition de règlement (sans DB)."""
        return ConditionReglement(
            code=f"T{base_jours}",
            libelle=f"Test {base_jours}j",
            base_jours=base_jours,
            fin_de_mois=fin_de_mois,
            jour_du_mois=jour_du_mois,
        )

    def test_30_jours_net(self):
        """30 jours net depuis le 15 janvier = 14 février."""
        term = self._make_term(30)
        result = self.calc.calculate(date(2026, 1, 15), term)
        assert result == date(2026, 2, 14)

    def test_60_jours_net(self):
        """60 jours net depuis le 1er mars = 30 avril."""
        term = self._make_term(60)
        result = self.calc.calculate(date(2026, 3, 1), term)
        assert result == date(2026, 4, 30)

    def test_30_jours_fin_de_mois(self):
        """30 jours fin de mois depuis le 15 janvier.
        15/01 + 30j = 14/02 -> fin février = 28/02."""
        term = self._make_term(30, fin_de_mois=True)
        result = self.calc.calculate(date(2026, 1, 15), term)
        assert result == date(2026, 2, 28)

    def test_30_jours_fin_de_mois_fevrier_bissextile(self):
        """30 jours fin de mois en année bissextile."""
        term = self._make_term(30, fin_de_mois=True)
        result = self.calc.calculate(date(2028, 1, 15), term)
        assert result == date(2028, 2, 29)

    def test_45_jours_fin_de_mois(self):
        """45 jours fin de mois depuis le 15 janvier.
        15/01 + 45j = 01/03 -> fin mars = 31/03."""
        term = self._make_term(45, fin_de_mois=True)
        result = self.calc.calculate(date(2026, 1, 15), term)
        assert result == date(2026, 3, 31)

    def test_45_jours_fin_de_mois_le_10(self):
        """45 jours fin de mois le 10 depuis le 15 janvier.
        15/01 + 45j = 01/03 -> fin mars = 31/03 -> 10 avril."""
        term = self._make_term(45, fin_de_mois=True, jour_du_mois=10)
        result = self.calc.calculate(date(2026, 1, 15), term)
        assert result == date(2026, 4, 10)

    def test_60_jours_fin_de_mois_le_15(self):
        """60 jours fin de mois le 15 depuis le 10 février.
        10/02 + 60j = 11/04 -> fin avril = 30/04 -> 15 mai."""
        term = self._make_term(60, fin_de_mois=True, jour_du_mois=15)
        result = self.calc.calculate(date(2026, 2, 10), term)
        assert result == date(2026, 5, 15)

    def test_90_jours_net(self):
        """90 jours net depuis le 1er janvier = 1er avril."""
        term = self._make_term(90)
        result = self.calc.calculate(date(2026, 1, 1), term)
        assert result == date(2026, 4, 1)

    def test_0_jours_comptant(self):
        """Paiement comptant (0 jours)."""
        term = self._make_term(0)
        result = self.calc.calculate(date(2026, 3, 15), term)
        assert result == date(2026, 3, 15)

    def test_passage_annee(self):
        """30 jours fin de mois depuis le 15 décembre.
        15/12 + 30j = 14/01 -> fin janvier = 31/01."""
        term = self._make_term(30, fin_de_mois=True)
        result = self.calc.calculate(date(2026, 12, 15), term)
        assert result == date(2027, 1, 31)

    def test_scenario_retard(self):
        """Ajustement scénario : +15 jours de retard."""
        base = date(2026, 2, 28)
        result = self.calc.calculate_with_scenario(base, 15)
        assert result == date(2026, 3, 15)

    def test_scenario_avance(self):
        """Ajustement scénario : -5 jours (encaissement anticipé)."""
        base = date(2026, 3, 20)
        result = self.calc.calculate_with_scenario(base, -5)
        assert result == date(2026, 3, 15)
