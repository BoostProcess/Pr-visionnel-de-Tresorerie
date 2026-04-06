"""Agrégation mensuelle des lignes de prévisionnel."""

from dataclasses import dataclass, field
from datetime import date
from collections import defaultdict

from app.models.cash import LignePrevisionnel


@dataclass
class MonthSummary:
    """Résumé d'un mois de prévisionnel."""
    mois: date
    tresorerie_debut: int = 0
    total_encaissements: int = 0
    total_decaissements: int = 0
    flux_net: int = 0
    tresorerie_fin: int = 0
    # Détails encaissements
    encaissements_factures: int = 0
    encaissements_commandes: int = 0
    avoirs_clients: int = 0
    # Détails décaissements
    decaissements_factures: int = 0
    decaissements_commandes: int = 0
    charges_fixes: int = 0
    emprunts: int = 0
    tva: int = 0
    charges_sociales: int = 0
    impots: int = 0
    avoirs_fournisseurs: int = 0
    ajustements: int = 0


class MonthlyAggregator:
    """Agrège les lignes de prévisionnel par mois et calcule les soldes glissants."""

    def aggregate(
        self, lines: list[LignePrevisionnel], initial_cash: int,
    ) -> list[MonthSummary]:
        """Agrège les lignes par mois et calcule la trésorerie glissante."""
        # Grouper par mois
        by_month: dict[date, list[LignePrevisionnel]] = defaultdict(list)
        for line in lines:
            by_month[line.mois].append(line)

        # Trier les mois
        sorted_months = sorted(by_month.keys())
        if not sorted_months:
            return []

        summaries = []
        current_cash = initial_cash

        for month_date in sorted_months:
            month_lines = by_month[month_date]
            summary = self._build_summary(month_date, month_lines)
            summary.tresorerie_debut = current_cash
            summary.tresorerie_fin = current_cash + summary.flux_net
            current_cash = summary.tresorerie_fin
            summaries.append(summary)

        return summaries

    def _build_summary(self, month_date: date, lines: list[LignePrevisionnel]) -> MonthSummary:
        """Construit le résumé d'un mois à partir de ses lignes."""
        summary = MonthSummary(mois=month_date)

        for line in lines:
            montant = line.montant
            cat = line.categorie

            if montant > 0:
                summary.total_encaissements += montant
            else:
                summary.total_decaissements += montant

            # Ventilation par catégorie
            if cat == "encaissement_facture":
                summary.encaissements_factures += montant
            elif cat == "encaissement_commande":
                summary.encaissements_commandes += montant
            elif cat == "avoir_client":
                summary.avoirs_clients += montant
            elif cat == "decaissement_facture":
                summary.decaissements_factures += montant
            elif cat == "decaissement_commande":
                summary.decaissements_commandes += montant
            elif cat == "charge_fixe":
                summary.charges_fixes += montant
            elif cat == "emprunt":
                summary.emprunts += montant
            elif cat == "tva":
                summary.tva += montant
            elif cat == "charges_sociales":
                summary.charges_sociales += montant
            elif cat == "impot":
                summary.impots += montant
            elif cat == "avoir_fournisseur":
                summary.avoirs_fournisseurs += montant
            elif cat == "ajustement_manuel":
                summary.ajustements += montant

        summary.flux_net = summary.total_encaissements + summary.total_decaissements
        return summary
