"""Moteur de projection des charges fixes, emprunts et taxes."""

from datetime import date

from sqlalchemy.orm import Session

from app.models.cash import LignePrevisionnel
from app.models.fixed_charges import ChargeFiscale, ChargeFix, Emprunt


class FixedChargeEngine:
    """Projette les charges fixes, emprunts et taxes sur la période."""

    def project_fixed_charges(
        self, session: Session, scenario: str, start_month: date, months: int,
    ) -> list[LignePrevisionnel]:
        """Génère les lignes pour toutes les charges fixes actives."""
        lines = []
        charges = session.query(ChargeFix).filter(ChargeFix.is_active == True).all()

        for charge in charges:
            for m in range(months):
                month_date = self._add_months(start_month, m)

                # Vérifier que la charge est active sur ce mois
                if charge.date_debut > month_date:
                    continue
                if charge.date_fin and charge.date_fin < month_date:
                    continue

                # Vérifier la fréquence
                if not self._is_payment_month(charge.frequence, month_date, charge.date_debut):
                    continue

                lines.append(
                    LignePrevisionnel(
                        scenario=scenario,
                        mois=month_date,
                        categorie="charge_fixe",
                        sous_categorie=charge.categorie,
                        source_type="charge_fixe",
                        source_id=charge.id,
                        nom_tiers=charge.libelle,
                        montant=-charge.montant_ttc,
                        date_echeance=month_date.replace(
                            day=min(charge.jour_paiement, 28)
                        ),
                    )
                )
        return lines

    def project_loans(
        self, session: Session, scenario: str, start_month: date, months: int,
    ) -> list[LignePrevisionnel]:
        """Génère les mensualités d'emprunts."""
        lines = []
        emprunts = session.query(Emprunt).filter(Emprunt.is_active == True).all()

        for emprunt in emprunts:
            for m in range(months):
                month_date = self._add_months(start_month, m)

                if emprunt.date_debut > month_date:
                    continue
                if emprunt.date_fin < month_date:
                    continue

                lines.append(
                    LignePrevisionnel(
                        scenario=scenario,
                        mois=month_date,
                        categorie="emprunt",
                        sous_categorie="mensualite",
                        source_type="emprunt",
                        source_id=emprunt.id,
                        nom_tiers=f"{emprunt.libelle} ({emprunt.preteur})",
                        montant=-emprunt.mensualite,
                        date_echeance=month_date.replace(
                            day=min(emprunt.jour_paiement, 28)
                        ),
                    )
                )
        return lines

    def project_taxes(
        self, session: Session, scenario: str, start_month: date, months: int,
    ) -> list[LignePrevisionnel]:
        """Génère les lignes pour les charges fiscales à montant fixe/estimé."""
        lines = []
        taxes = (
            session.query(ChargeFiscale)
            .filter(ChargeFiscale.is_active == True)
            .filter(ChargeFiscale.methode_calcul == "fixe")
            .all()
        )

        for tax in taxes:
            if not tax.montant_estime:
                continue

            for m in range(months):
                month_date = self._add_months(start_month, m)

                if not self._is_payment_month(tax.frequence, month_date, start_month):
                    continue

                lines.append(
                    LignePrevisionnel(
                        scenario=scenario,
                        mois=month_date,
                        categorie=tax.type_taxe,
                        sous_categorie=tax.libelle,
                        source_type="charge_fiscale",
                        source_id=tax.id,
                        nom_tiers=tax.libelle,
                        montant=-tax.montant_estime,
                        date_echeance=month_date.replace(day=15),
                    )
                )
        return lines

    @staticmethod
    def _add_months(start: date, months: int) -> date:
        """Ajoute N mois à une date (retourne le 1er du mois)."""
        month = start.month + months
        year = start.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        return date(year, month, 1)

    @staticmethod
    def _is_payment_month(frequence: str, month_date: date, reference_date: date) -> bool:
        """Vérifie si le mois est un mois de paiement selon la fréquence."""
        if frequence == "mensuel":
            return True
        elif frequence == "trimestriel":
            # Tous les 3 mois à partir de la date de référence
            diff = (month_date.year - reference_date.year) * 12 + (
                month_date.month - reference_date.month
            )
            return diff % 3 == 0
        elif frequence == "annuel":
            return month_date.month == reference_date.month
        return False
