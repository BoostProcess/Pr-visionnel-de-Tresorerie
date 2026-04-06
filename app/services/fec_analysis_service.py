"""Service d'analyse financière à partir des écritures FEC.

Fournit :
- Compte de résultat reconstitué
- Soldes Intermédiaires de Gestion (SIG)
- KPIs financiers (BFR, DSO, DPO, marge, EBE, CAF)
- Balance âgée clients et fournisseurs
- Tableau de flux de trésorerie (méthode indirecte)
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.fec_entry import EcritureFEC
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.reference import Client, Fournisseur


# ──────────────────────────────────────────────────────────
# Dataclasses de résultat
# ──────────────────────────────────────────────────────────

@dataclass
class LigneCompteResultat:
    code: str
    libelle: str
    montant: int = 0


@dataclass
class CompteResultat:
    """Compte de résultat simplifié reconstitué depuis le FEC."""
    chiffre_affaires: int = 0
    achats: int = 0
    variation_stocks: int = 0
    autres_produits: int = 0
    charges_externes: int = 0
    impots_taxes: int = 0
    charges_personnel: int = 0
    dotations_amortissements: int = 0
    produits_financiers: int = 0
    charges_financieres: int = 0
    produits_exceptionnels: int = 0
    charges_exceptionnelles: int = 0
    impot_benefice: int = 0
    detail: list[LigneCompteResultat] = field(default_factory=list)

    @property
    def marge_brute(self) -> int:
        return self.chiffre_affaires - self.achats - self.variation_stocks

    @property
    def valeur_ajoutee(self) -> int:
        return self.marge_brute - self.charges_externes + self.autres_produits

    @property
    def ebe(self) -> int:
        """Excédent Brut d'Exploitation."""
        return self.valeur_ajoutee - self.impots_taxes - self.charges_personnel

    @property
    def resultat_exploitation(self) -> int:
        return self.ebe - self.dotations_amortissements

    @property
    def resultat_financier(self) -> int:
        return self.produits_financiers - self.charges_financieres

    @property
    def resultat_courant(self) -> int:
        return self.resultat_exploitation + self.resultat_financier

    @property
    def resultat_exceptionnel(self) -> int:
        return self.produits_exceptionnels - self.charges_exceptionnelles

    @property
    def resultat_net(self) -> int:
        return self.resultat_courant + self.resultat_exceptionnel - self.impot_benefice

    @property
    def caf(self) -> int:
        """Capacité d'Autofinancement = Résultat net + Dotations amortissements."""
        return self.resultat_net + self.dotations_amortissements


@dataclass
class KPIsFinanciers:
    """Indicateurs clés de pilotage."""
    chiffre_affaires: int = 0
    marge_brute: int = 0
    taux_marge_brute: float = 0.0
    valeur_ajoutee: int = 0
    ebe: int = 0
    taux_ebe: float = 0.0
    resultat_net: int = 0
    caf: int = 0
    bfr: int = 0
    creances_clients: int = 0
    dettes_fournisseurs: int = 0
    dso_jours: int = 0  # Days Sales Outstanding (délai clients)
    dpo_jours: int = 0  # Days Payable Outstanding (délai fournisseurs)
    tresorerie_nette: int = 0


@dataclass
class LigneBalanceAgee:
    """Ligne de balance âgée pour un tiers."""
    code: str
    nom: str
    total: int = 0
    non_echu: int = 0
    echu_0_30: int = 0
    echu_30_60: int = 0
    echu_60_90: int = 0
    echu_plus_90: int = 0


@dataclass
class FluxTresorerie:
    """Tableau de flux de trésorerie (méthode indirecte)."""
    # Flux d'exploitation
    resultat_net: int = 0
    dotations_amortissements: int = 0
    variation_stocks: int = 0
    variation_creances: int = 0
    variation_dettes: int = 0

    # Flux d'investissement
    acquisitions_immo: int = 0
    cessions_immo: int = 0

    # Flux de financement
    emprunts_nouveaux: int = 0
    remboursements_emprunts: int = 0
    apports_capital: int = 0
    dividendes: int = 0

    @property
    def flux_exploitation(self) -> int:
        return (self.resultat_net + self.dotations_amortissements
                - self.variation_stocks - self.variation_creances
                + self.variation_dettes)

    @property
    def flux_investissement(self) -> int:
        return self.cessions_immo - self.acquisitions_immo

    @property
    def flux_financement(self) -> int:
        return (self.emprunts_nouveaux - self.remboursements_emprunts
                + self.apports_capital - self.dividendes)

    @property
    def variation_tresorerie(self) -> int:
        return self.flux_exploitation + self.flux_investissement + self.flux_financement


# ──────────────────────────────────────────────────────────
# Service d'analyse
# ──────────────────────────────────────────────────────────

class FECAnalysisService:
    """Analyse financière à partir des écritures FEC stockées en base."""

    def __init__(self, session: Session):
        self._session = session

    def has_fec_data(self) -> bool:
        """Vérifie si des écritures FEC existent en base."""
        return self._session.query(EcritureFEC).count() > 0

    # ── Compte de résultat ──

    def compute_compte_resultat(
        self, date_debut: date | None = None, date_fin: date | None = None
    ) -> CompteResultat:
        """Reconstitue le compte de résultat depuis les écritures FEC.

        Classification par numéro de compte PCG :
        - 70x : Ventes / Chiffre d'affaires
        - 60x : Achats et variation de stocks
        - 61x/62x : Charges externes
        - 63x : Impôts et taxes
        - 64x : Charges de personnel
        - 65x : Autres charges de gestion
        - 66x : Charges financières
        - 67x : Charges exceptionnelles
        - 68x : Dotations aux amortissements
        - 69x : Impôt sur les bénéfices
        - 71x : Production stockée
        - 72x : Production immobilisée
        - 74x : Subventions
        - 75x : Autres produits de gestion
        - 76x : Produits financiers
        - 77x : Produits exceptionnels
        - 78x : Reprises amortissements/provisions
        """
        query = self._session.query(EcritureFEC)
        if date_debut:
            query = query.filter(EcritureFEC.ecriture_date >= date_debut)
        if date_fin:
            query = query.filter(EcritureFEC.ecriture_date <= date_fin)

        ecritures = query.all()
        cr = CompteResultat()

        # Agréger par préfixe de compte (classes 6 et 7)
        for e in ecritures:
            compte = e.compte_num
            solde = e.credit - e.debit  # Produits en crédit, charges en débit

            if not compte:
                continue

            prefix2 = compte[:2]
            prefix3 = compte[:3] if len(compte) >= 3 else prefix2

            # Classe 7 : Produits
            if compte.startswith("70"):
                cr.chiffre_affaires += solde
            elif compte.startswith("71") or compte.startswith("72"):
                cr.variation_stocks += solde
            elif prefix2 in ("74", "75"):
                cr.autres_produits += solde
            elif compte.startswith("76"):
                cr.produits_financiers += solde
            elif compte.startswith("77"):
                cr.produits_exceptionnels += solde
            elif compte.startswith("78"):
                cr.dotations_amortissements -= solde  # Reprises = réduction des dotations

            # Classe 6 : Charges (débit = montant positif)
            elif prefix2 in ("60",):
                cr.achats += (e.debit - e.credit)
            elif prefix2 in ("61", "62"):
                cr.charges_externes += (e.debit - e.credit)
            elif prefix2 == "63":
                cr.impots_taxes += (e.debit - e.credit)
            elif prefix2 == "64":
                cr.charges_personnel += (e.debit - e.credit)
            elif prefix2 == "65":
                cr.charges_externes += (e.debit - e.credit)  # Autres charges gestion
            elif prefix2 == "66":
                cr.charges_financieres += (e.debit - e.credit)
            elif prefix2 == "67":
                cr.charges_exceptionnelles += (e.debit - e.credit)
            elif prefix2 == "68":
                cr.dotations_amortissements += (e.debit - e.credit)
            elif prefix2 == "69":
                cr.impot_benefice += (e.debit - e.credit)

        return cr

    # ── KPIs ──

    def compute_kpis(
        self, date_debut: date | None = None, date_fin: date | None = None
    ) -> KPIsFinanciers:
        """Calcule les KPIs financiers."""
        cr = self.compute_compte_resultat(date_debut, date_fin)

        # Créances clients (reste à régler)
        creances = self._session.query(
            func.coalesce(func.sum(FactureClient.reste_a_regler), 0)
        ).filter(FactureClient.statut.in_(["ouvert", "partiel"])).scalar()

        # Dettes fournisseurs (reste à régler)
        dettes = self._session.query(
            func.coalesce(func.sum(FactureFournisseur.reste_a_regler), 0)
        ).filter(FactureFournisseur.statut.in_(["ouvert", "partiel"])).scalar()

        # BFR = Créances clients - Dettes fournisseurs
        bfr = creances - dettes

        # DSO = (Créances clients / CA) * 365
        ca = max(cr.chiffre_affaires, 1)
        nb_jours = self._nb_jours_periode(date_debut, date_fin)
        dso = round((creances / ca) * nb_jours) if ca > 0 else 0
        dpo = round((dettes / cr.achats) * nb_jours) if cr.achats > 0 else 0

        # Trésorerie nette (comptes 5xx)
        treso = self._solde_comptes_tresorerie()

        return KPIsFinanciers(
            chiffre_affaires=cr.chiffre_affaires,
            marge_brute=cr.marge_brute,
            taux_marge_brute=round(cr.marge_brute / ca * 100, 1) if ca > 0 else 0.0,
            valeur_ajoutee=cr.valeur_ajoutee,
            ebe=cr.ebe,
            taux_ebe=round(cr.ebe / ca * 100, 1) if ca > 0 else 0.0,
            resultat_net=cr.resultat_net,
            caf=cr.caf,
            bfr=bfr,
            creances_clients=creances,
            dettes_fournisseurs=dettes,
            dso_jours=dso,
            dpo_jours=dpo,
            tresorerie_nette=treso,
        )

    # ── Balance âgée ──

    def compute_balance_agee_clients(self) -> list[LigneBalanceAgee]:
        """Balance âgée des créances clients."""
        today = date.today()
        factures = (
            self._session.query(FactureClient)
            .filter(FactureClient.statut.in_(["ouvert", "partiel"]))
            .all()
        )

        par_client: dict[int, LigneBalanceAgee] = {}
        client_cache: dict[int, tuple[str, str]] = {}

        for f in factures:
            if f.client_id not in client_cache:
                client = self._session.get(Client, f.client_id)
                if client:
                    client_cache[f.client_id] = (client.sage_code, client.name)
                else:
                    client_cache[f.client_id] = ("???", "Inconnu")

            if f.client_id not in par_client:
                code, nom = client_cache[f.client_id]
                par_client[f.client_id] = LigneBalanceAgee(code=code, nom=nom)

            ligne = par_client[f.client_id]
            montant = f.reste_a_regler
            ligne.total += montant

            echeance = f.date_echeance or f.date_facture
            jours_retard = (today - echeance).days

            if jours_retard <= 0:
                ligne.non_echu += montant
            elif jours_retard <= 30:
                ligne.echu_0_30 += montant
            elif jours_retard <= 60:
                ligne.echu_30_60 += montant
            elif jours_retard <= 90:
                ligne.echu_60_90 += montant
            else:
                ligne.echu_plus_90 += montant

        return sorted(par_client.values(), key=lambda l: l.total, reverse=True)

    def compute_balance_agee_fournisseurs(self) -> list[LigneBalanceAgee]:
        """Balance âgée des dettes fournisseurs."""
        today = date.today()
        factures = (
            self._session.query(FactureFournisseur)
            .filter(FactureFournisseur.statut.in_(["ouvert", "partiel"]))
            .all()
        )

        par_fournisseur: dict[int, LigneBalanceAgee] = {}
        four_cache: dict[int, tuple[str, str]] = {}

        for f in factures:
            if f.fournisseur_id not in four_cache:
                four = self._session.get(Fournisseur, f.fournisseur_id)
                if four:
                    four_cache[f.fournisseur_id] = (four.sage_code, four.name)
                else:
                    four_cache[f.fournisseur_id] = ("???", "Inconnu")

            if f.fournisseur_id not in par_fournisseur:
                code, nom = four_cache[f.fournisseur_id]
                par_fournisseur[f.fournisseur_id] = LigneBalanceAgee(code=code, nom=nom)

            ligne = par_fournisseur[f.fournisseur_id]
            montant = f.reste_a_regler
            ligne.total += montant

            echeance = f.date_echeance or f.date_facture
            jours_retard = (today - echeance).days

            if jours_retard <= 0:
                ligne.non_echu += montant
            elif jours_retard <= 30:
                ligne.echu_0_30 += montant
            elif jours_retard <= 60:
                ligne.echu_30_60 += montant
            elif jours_retard <= 90:
                ligne.echu_60_90 += montant
            else:
                ligne.echu_plus_90 += montant

        return sorted(par_fournisseur.values(), key=lambda l: l.total, reverse=True)

    # ── Tableau de flux de trésorerie ──

    def compute_flux_tresorerie(
        self, date_debut: date | None = None, date_fin: date | None = None
    ) -> FluxTresorerie:
        """Tableau de flux de trésorerie (méthode indirecte)."""
        cr = self.compute_compte_resultat(date_debut, date_fin)

        query = self._session.query(EcritureFEC)
        if date_debut:
            query = query.filter(EcritureFEC.ecriture_date >= date_debut)
        if date_fin:
            query = query.filter(EcritureFEC.ecriture_date <= date_fin)

        ecritures = query.all()

        ft = FluxTresorerie()
        ft.resultat_net = cr.resultat_net
        ft.dotations_amortissements = cr.dotations_amortissements

        # Analyser les mouvements de bilan
        for e in ecritures:
            compte = e.compte_num
            mouvement = e.debit - e.credit

            if compte.startswith("3"):  # Stocks
                ft.variation_stocks += mouvement
            elif compte.startswith("41"):  # Créances clients
                ft.variation_creances += mouvement
            elif compte.startswith("40"):  # Dettes fournisseurs
                ft.variation_dettes -= mouvement  # Augmentation dette = + flux
            elif compte.startswith("2") and not compte.startswith("28"):  # Immobilisations
                if mouvement > 0:
                    ft.acquisitions_immo += mouvement
                else:
                    ft.cessions_immo += abs(mouvement)
            elif compte.startswith("16"):  # Emprunts
                if mouvement < 0:  # Crédit = nouvel emprunt
                    ft.emprunts_nouveaux += abs(mouvement)
                else:
                    ft.remboursements_emprunts += mouvement
            elif compte.startswith("10"):  # Capital
                ft.apports_capital -= mouvement  # Crédit = apport
            elif compte.startswith("457"):  # Dividendes
                ft.dividendes += mouvement

        return ft

    # ── Compte de résultat par mois (pour comparaison N/N-1) ──

    def compute_ca_mensuel(
        self, date_debut: date | None = None, date_fin: date | None = None
    ) -> dict[str, int]:
        """Chiffre d'affaires par mois."""
        query = self._session.query(
            func.substr(
                func.cast(EcritureFEC.ecriture_date, String), 1, 7
            ).label("mois"),
            func.sum(EcritureFEC.credit - EcritureFEC.debit).label("montant"),
        ).filter(
            EcritureFEC.compte_num.like("70%")
        ).group_by("mois")

        if date_debut:
            query = query.filter(EcritureFEC.ecriture_date >= date_debut)
        if date_fin:
            query = query.filter(EcritureFEC.ecriture_date <= date_fin)

        return {row.mois: int(row.montant) for row in query.all()}

    # ── Méthodes utilitaires ──

    def _solde_comptes_tresorerie(self) -> int:
        """Solde des comptes de trésorerie (classe 5)."""
        result = self._session.query(
            func.coalesce(
                func.sum(EcritureFEC.debit - EcritureFEC.credit), 0
            )
        ).filter(
            EcritureFEC.compte_num.like("5%")
        ).scalar()
        return int(result)

    @staticmethod
    def _nb_jours_periode(date_debut: date | None, date_fin: date | None) -> int:
        if date_debut and date_fin:
            return max((date_fin - date_debut).days, 1)
        return 365


# Nécessaire pour le type cast dans la requête SQLite
from sqlalchemy import String  # noqa: E402
