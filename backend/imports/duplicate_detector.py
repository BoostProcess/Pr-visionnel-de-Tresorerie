"""Détection de doublons lors de l'import."""

from sqlalchemy.orm import Session

from app.models.invoices import Avoir, FactureClient, FactureFournisseur
from app.models.orders import CommandeClient, CommandeFournisseur
from app.models.reference import Client, Fournisseur


class DuplicateDetector:
    """Détecte les doublons par rapport aux données existantes en base."""

    def __init__(self, session: Session):
        self._session = session
        self._cache: dict[str, set[str]] = {}

    def build_cache(self, file_type: str):
        """Pré-charge les clés existantes pour un type donné."""
        model_map = {
            "clients": (Client, "sage_code"),
            "fournisseurs": (Fournisseur, "sage_code"),
            "factures_clients": (FactureClient, "sage_doc_number"),
            "factures_fournisseurs": (FactureFournisseur, "sage_doc_number"),
            "commandes_clients": (CommandeClient, "sage_doc_number"),
            "commandes_fournisseurs": (CommandeFournisseur, "sage_doc_number"),
            "avoirs": (Avoir, "sage_doc_number"),
        }

        if file_type not in model_map:
            self._cache[file_type] = set()
            return

        model_class, field_name = model_map[file_type]
        column = getattr(model_class, field_name)
        existing = self._session.query(column).all()
        self._cache[file_type] = {row[0] for row in existing}

    def is_duplicate(self, file_type: str, key_value: str) -> bool:
        """Vérifie si une clé existe déjà."""
        if file_type not in self._cache:
            self.build_cache(file_type)
        return key_value in self._cache[file_type]

    def add_to_cache(self, file_type: str, key_value: str):
        """Ajoute une clé au cache (après insertion réussie)."""
        if file_type not in self._cache:
            self._cache[file_type] = set()
        self._cache[file_type].add(key_value)

    @staticmethod
    def get_key_field(file_type: str) -> str:
        """Retourne le nom du champ clé pour la détection de doublons."""
        key_fields = {
            "clients": "sage_code",
            "fournisseurs": "sage_code",
            "factures_clients": "sage_doc_number",
            "factures_fournisseurs": "sage_doc_number",
            "commandes_clients": "sage_doc_number",
            "commandes_fournisseurs": "sage_doc_number",
            "avoirs": "sage_doc_number",
            "historique": "tiers_sage_code",
        }
        return key_fields.get(file_type, "sage_code")
