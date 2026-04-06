"""Moteur de calcul TVA Polynésie Française."""

from datetime import date

from app.models.cash import LignePrevisionnel
from config import TVA_RATES


class VATEngine:
    """Calcule la TVA à décaisser mensuellement.

    Régime mensuel (CA3 PF) :
    - TVA collectée sur les encaissements du mois M
    - TVA déductible sur les décaissements du mois M
    - TVA nette = collectée - déductible
    - Si positive : décaissement le mois M+1
    - Si négative : crédit reporté
    """

    def compute_vat_payments(
        self,
        all_lines: list[LignePrevisionnel],
        scenario: str,
        start_month: date,
        months: int,
    ) -> list[LignePrevisionnel]:
        """Calcule les décaissements de TVA à partir des lignes existantes."""
        lines = []
        credit_tva = 0  # Crédit de TVA reporté

        for m in range(months):
            month_date = self._add_months(start_month, m)

            # Calculer TVA collectée (sur encaissements)
            tva_collectee = 0
            for line in all_lines:
                if line.mois == month_date and line.montant > 0:
                    tva_collectee += self._estimate_vat(line.montant)

            # Calculer TVA déductible (sur décaissements hors TVA et emprunts)
            tva_deductible = 0
            for line in all_lines:
                if line.mois == month_date and line.montant < 0:
                    if line.categorie not in ("tva", "emprunt", "charges_sociales", "impot"):
                        tva_deductible += self._estimate_vat(abs(line.montant))

            # TVA nette
            tva_nette = tva_collectee - tva_deductible - credit_tva

            if tva_nette > 0:
                # Décaissement TVA le mois suivant
                payment_month = self._add_months(month_date, 1)
                if payment_month < self._add_months(start_month, months):
                    lines.append(
                        LignePrevisionnel(
                            scenario=scenario,
                            mois=payment_month,
                            categorie="tva",
                            sous_categorie="tva_nette",
                            source_type="calcul_tva",
                            nom_tiers="TVA PF",
                            montant=-int(tva_nette),
                            date_echeance=payment_month.replace(day=20),
                            notes=f"TVA collectée: {tva_collectee}, déductible: {tva_deductible}",
                        )
                    )
                credit_tva = 0
            else:
                # Crédit de TVA reporté
                credit_tva = abs(tva_nette)

        return lines

    @staticmethod
    def _estimate_vat(montant_ttc: int) -> int:
        """Estime la TVA contenue dans un montant TTC (taux normal PF 16%)."""
        taux = TVA_RATES["normal"]
        return int(montant_ttc * taux / (1 + taux))

    @staticmethod
    def _add_months(start: date, months: int) -> date:
        month = start.month + months
        year = start.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        return date(year, month, 1)
