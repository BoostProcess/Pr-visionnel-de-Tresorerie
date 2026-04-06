"""Chargement des données validées en base."""

from sqlalchemy.orm import Session

from app.models.history import HistoriqueFacturation
from app.models.invoices import Avoir, FactureClient, FactureFournisseur
from app.models.orders import CommandeClient, CommandeFournisseur
from app.models.reference import Client, ConditionReglement, Fournisseur


class DataLoader:
    """Insère les lignes validées dans la base de données."""

    def __init__(self, session: Session):
        self._session = session
        self._condition_cache: dict[str, int] = {}
        self._client_cache: dict[str, int] = {}
        self._fournisseur_cache: dict[str, int] = {}

    def build_reference_caches(self):
        """Pré-charge les caches de référence."""
        for cr in self._session.query(ConditionReglement).all():
            self._condition_cache[cr.code] = cr.id
        for c in self._session.query(Client).all():
            self._client_cache[c.sage_code] = c.id
        for f in self._session.query(Fournisseur).all():
            self._fournisseur_cache[f.sage_code] = f.id

    def load_row(self, row: dict, file_type: str, lot_import_id: int) -> bool:
        """Insère une ligne. Retourne True si succès."""
        method = getattr(self, f"_load_{file_type}", None)
        if method is None:
            return False
        return method(row, lot_import_id)

    def _load_clients(self, row: dict, lot_import_id: int) -> bool:
        cr_id = self._condition_cache.get(row.get("condition_reglement_code"))
        client = Client(
            sage_code=row["sage_code"],
            name=row["name"],
            condition_reglement_id=cr_id,
            code_activite=row.get("code_activite"),
            is_active=row.get("is_active", True),
        )
        self._session.add(client)
        self._session.flush()
        self._client_cache[client.sage_code] = client.id
        return True

    def _load_fournisseurs(self, row: dict, lot_import_id: int) -> bool:
        cr_id = self._condition_cache.get(row.get("condition_reglement_code"))
        fournisseur = Fournisseur(
            sage_code=row["sage_code"],
            name=row["name"],
            condition_reglement_id=cr_id,
            code_activite=row.get("code_activite"),
            is_active=row.get("is_active", True),
        )
        self._session.add(fournisseur)
        self._session.flush()
        self._fournisseur_cache[fournisseur.sage_code] = fournisseur.id
        return True

    def _load_factures_clients(self, row: dict, lot_import_id: int) -> bool:
        client_id = self._client_cache.get(row.get("client_sage_code"))
        if client_id is None:
            return False

        montant_ttc = row.get("montant_ttc", 0)
        montant_ht = row.get("montant_ht", 0)
        montant_regle = row.get("montant_regle", 0)
        reste = montant_ttc - montant_regle

        statut = "ouvert"
        if reste <= 0:
            statut = "regle"
        elif montant_regle > 0:
            statut = "partiel"

        facture = FactureClient(
            sage_doc_number=row["sage_doc_number"],
            sage_doc_type=int(row.get("sage_doc_type", 6)),
            client_id=client_id,
            date_facture=row["date_facture"],
            date_echeance=row.get("date_echeance"),
            montant_ht=montant_ht,
            montant_ttc=montant_ttc,
            montant_tva=montant_ttc - montant_ht,
            montant_regle=montant_regle,
            reste_a_regler=reste,
            code_affaire=row.get("code_affaire"),
            statut=statut,
            lot_import_id=lot_import_id,
        )
        self._session.add(facture)
        return True

    def _load_factures_fournisseurs(self, row: dict, lot_import_id: int) -> bool:
        fournisseur_id = self._fournisseur_cache.get(row.get("fournisseur_sage_code"))
        if fournisseur_id is None:
            return False

        montant_ttc = row.get("montant_ttc", 0)
        montant_ht = row.get("montant_ht", 0)
        montant_regle = row.get("montant_regle", 0)
        reste = montant_ttc - montant_regle

        statut = "ouvert"
        if reste <= 0:
            statut = "regle"
        elif montant_regle > 0:
            statut = "partiel"

        facture = FactureFournisseur(
            sage_doc_number=row["sage_doc_number"],
            sage_doc_type=int(row.get("sage_doc_type", 6)),
            fournisseur_id=fournisseur_id,
            date_facture=row["date_facture"],
            date_echeance=row.get("date_echeance"),
            montant_ht=montant_ht,
            montant_ttc=montant_ttc,
            montant_tva=montant_ttc - montant_ht,
            montant_regle=montant_regle,
            reste_a_regler=reste,
            code_affaire=row.get("code_affaire"),
            statut=statut,
            lot_import_id=lot_import_id,
        )
        self._session.add(facture)
        return True

    def _load_commandes_clients(self, row: dict, lot_import_id: int) -> bool:
        client_id = self._client_cache.get(row.get("client_sage_code"))
        if client_id is None:
            return False

        montant_ttc = row.get("montant_ttc", 0)
        montant_ht = row.get("montant_ht", 0)

        commande = CommandeClient(
            sage_doc_number=row["sage_doc_number"],
            client_id=client_id,
            date_commande=row["date_commande"],
            date_facturation_prevue=row.get("date_facturation_prevue"),
            montant_ht=montant_ht,
            montant_ttc=montant_ttc,
            montant_facture=0,
            reste_a_facturer=montant_ttc,
            code_affaire=row.get("code_affaire"),
            statut="ouverte",
            lot_import_id=lot_import_id,
        )
        self._session.add(commande)
        return True

    def _load_commandes_fournisseurs(self, row: dict, lot_import_id: int) -> bool:
        fournisseur_id = self._fournisseur_cache.get(row.get("fournisseur_sage_code"))
        if fournisseur_id is None:
            return False

        montant_ttc = row.get("montant_ttc", 0)
        montant_ht = row.get("montant_ht", 0)

        commande = CommandeFournisseur(
            sage_doc_number=row["sage_doc_number"],
            fournisseur_id=fournisseur_id,
            date_commande=row["date_commande"],
            date_facturation_prevue=row.get("date_facturation_prevue"),
            montant_ht=montant_ht,
            montant_ttc=montant_ttc,
            montant_facture=0,
            reste_a_facturer=montant_ttc,
            code_affaire=row.get("code_affaire"),
            statut="ouverte",
            lot_import_id=lot_import_id,
        )
        self._session.add(commande)
        return True

    def _load_avoirs(self, row: dict, lot_import_id: int) -> bool:
        tiers_code = row.get("tiers_sage_code", "")
        type_tiers = "client"
        tiers_id = self._client_cache.get(tiers_code)
        if tiers_id is None:
            type_tiers = "fournisseur"
            tiers_id = self._fournisseur_cache.get(tiers_code)
        if tiers_id is None:
            return False

        avoir = Avoir(
            sage_doc_number=row["sage_doc_number"],
            type_tiers=type_tiers,
            tiers_id=tiers_id,
            date_avoir=row["date_avoir"],
            montant_ht=row.get("montant_ht", 0),
            montant_ttc=row.get("montant_ttc", 0),
            lot_import_id=lot_import_id,
        )
        self._session.add(avoir)
        return True

    def _load_historique(self, row: dict, lot_import_id: int) -> bool:
        tiers_code = row.get("tiers_sage_code", "")
        type_tiers = "client"
        tiers_id = self._client_cache.get(tiers_code)
        if tiers_id is None:
            type_tiers = "fournisseur"
            tiers_id = self._fournisseur_cache.get(tiers_code)
        if tiers_id is None:
            return False

        historique = HistoriqueFacturation(
            type_tiers=type_tiers,
            tiers_id=tiers_id,
            mois=row["mois"],
            montant_ht=row.get("montant_ht", 0),
            montant_ttc=row.get("montant_ttc", 0),
            nombre_factures=int(row.get("nombre_factures", 0)),
            delai_paiement_moyen_jours=row.get("delai_paiement_moyen_jours"),
            lot_import_id=lot_import_id,
        )
        self._session.add(historique)
        return True
