"""Validation des lignes importées."""

from datetime import date


class RowValidator:
    """Valide une ligne importée selon son type."""

    def validate(self, row: dict, file_type: str) -> list[str]:
        """Retourne la liste des erreurs. Vide = valide."""
        method = getattr(self, f"_validate_{file_type}", None)
        if method is None:
            return [f"Type de fichier inconnu : {file_type}"]
        return method(row)

    def _validate_clients(self, row: dict) -> list[str]:
        errors = []
        if not row.get("sage_code"):
            errors.append("Code Sage (CT_Num) manquant")
        if not row.get("name"):
            errors.append("Nom (CT_Intitule) manquant")
        return errors

    def _validate_fournisseurs(self, row: dict) -> list[str]:
        return self._validate_clients(row)

    def _validate_factures_clients(self, row: dict) -> list[str]:
        errors = []
        if not row.get("sage_doc_number"):
            errors.append("Numéro de pièce (DO_Piece) manquant")
        if not row.get("client_sage_code"):
            errors.append("Code client (CT_Num) manquant")
        if not isinstance(row.get("date_facture"), date):
            errors.append("Date de facture invalide ou manquante")
        montant_ttc = row.get("montant_ttc", 0)
        if not isinstance(montant_ttc, int) or montant_ttc == 0:
            errors.append("Montant TTC invalide ou nul")
        return errors

    def _validate_factures_fournisseurs(self, row: dict) -> list[str]:
        errors = []
        if not row.get("sage_doc_number"):
            errors.append("Numéro de pièce (DO_Piece) manquant")
        if not row.get("fournisseur_sage_code"):
            errors.append("Code fournisseur (CT_Num) manquant")
        if not isinstance(row.get("date_facture"), date):
            errors.append("Date de facture invalide ou manquante")
        montant_ttc = row.get("montant_ttc", 0)
        if not isinstance(montant_ttc, int) or montant_ttc == 0:
            errors.append("Montant TTC invalide ou nul")
        return errors

    def _validate_commandes_clients(self, row: dict) -> list[str]:
        errors = []
        if not row.get("sage_doc_number"):
            errors.append("Numéro de pièce (DO_Piece) manquant")
        if not row.get("client_sage_code"):
            errors.append("Code client (CT_Num) manquant")
        if not isinstance(row.get("date_commande"), date):
            errors.append("Date de commande invalide ou manquante")
        return errors

    def _validate_commandes_fournisseurs(self, row: dict) -> list[str]:
        errors = []
        if not row.get("sage_doc_number"):
            errors.append("Numéro de pièce (DO_Piece) manquant")
        if not row.get("fournisseur_sage_code"):
            errors.append("Code fournisseur (CT_Num) manquant")
        if not isinstance(row.get("date_commande"), date):
            errors.append("Date de commande invalide ou manquante")
        return errors

    def _validate_avoirs(self, row: dict) -> list[str]:
        errors = []
        if not row.get("sage_doc_number"):
            errors.append("Numéro de pièce (DO_Piece) manquant")
        if not row.get("tiers_sage_code"):
            errors.append("Code tiers (CT_Num) manquant")
        if not isinstance(row.get("date_avoir"), date):
            errors.append("Date d'avoir invalide ou manquante")
        return errors

    def _validate_historique(self, row: dict) -> list[str]:
        errors = []
        if not row.get("tiers_sage_code"):
            errors.append("Code tiers (CT_Num) manquant")
        if not isinstance(row.get("mois"), date):
            errors.append("Mois invalide ou manquant")
        return errors
