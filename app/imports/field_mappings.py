"""Mappings des colonnes Sage 100 vers les champs du modèle interne.

Chaque dictionnaire mappe le nom de colonne dans l'export Sage
vers le nom de champ dans notre modèle SQLAlchemy.
L'utilisateur peut personnaliser ces mappings via l'interface.
"""

CLIENT_FIELDS = {
    "CT_Num": "sage_code",
    "CT_Intitule": "name",
    "CT_Sommeil": "is_inactive",
    "N_Condition": "condition_reglement_code",
    "CT_Classement": "code_activite",
}

FOURNISSEUR_FIELDS = {
    "CT_Num": "sage_code",
    "CT_Intitule": "name",
    "CT_Sommeil": "is_inactive",
    "N_Condition": "condition_reglement_code",
    "CT_Classement": "code_activite",
}

FACTURE_CLIENT_FIELDS = {
    "DO_Piece": "sage_doc_number",
    "DO_Type": "sage_doc_type",
    "DO_Date": "date_facture",
    "DO_DateLivr": "date_echeance",
    "CT_Num": "client_sage_code",
    "DO_TotalHT": "montant_ht",
    "DO_TotalTTC": "montant_ttc",
    "DO_MontantRegle": "montant_regle",
    "DO_Ref": "code_affaire",
}

FACTURE_FOURNISSEUR_FIELDS = {
    "DO_Piece": "sage_doc_number",
    "DO_Type": "sage_doc_type",
    "DO_Date": "date_facture",
    "DO_DateLivr": "date_echeance",
    "CT_Num": "fournisseur_sage_code",
    "DO_TotalHT": "montant_ht",
    "DO_TotalTTC": "montant_ttc",
    "DO_MontantRegle": "montant_regle",
    "DO_Ref": "code_affaire",
}

COMMANDE_CLIENT_FIELDS = {
    "DO_Piece": "sage_doc_number",
    "DO_Date": "date_commande",
    "DO_DateLivr": "date_facturation_prevue",
    "CT_Num": "client_sage_code",
    "DO_TotalHT": "montant_ht",
    "DO_TotalTTC": "montant_ttc",
    "DO_Ref": "code_affaire",
}

COMMANDE_FOURNISSEUR_FIELDS = {
    "DO_Piece": "sage_doc_number",
    "DO_Date": "date_commande",
    "DO_DateLivr": "date_facturation_prevue",
    "CT_Num": "fournisseur_sage_code",
    "DO_TotalHT": "montant_ht",
    "DO_TotalTTC": "montant_ttc",
    "DO_Ref": "code_affaire",
}

AVOIR_FIELDS = {
    "DO_Piece": "sage_doc_number",
    "DO_Date": "date_avoir",
    "CT_Num": "tiers_sage_code",
    "DO_TotalHT": "montant_ht",
    "DO_TotalTTC": "montant_ttc",
    "DO_Ref": "facture_liee_ref",
}

HISTORIQUE_FIELDS = {
    "CT_Num": "tiers_sage_code",
    "Mois": "mois",
    "MontantHT": "montant_ht",
    "MontantTTC": "montant_ttc",
    "NbFactures": "nombre_factures",
    "DelaiMoyen": "delai_paiement_moyen_jours",
}

# FEC (Fichier des Écritures Comptables) - format réglementaire
# Fichier TXT tabulé, colonnes standardisées par l'administration fiscale
FEC_FIELDS = {
    "JournalCode": "journal_code",
    "JournalLib": "journal_lib",
    "EcritureNum": "ecriture_num",
    "EcritureDate": "ecriture_date",
    "CompteNum": "compte_num",
    "CompteLib": "compte_lib",
    "CompAuxNum": "comp_aux_num",
    "CompAuxLib": "comp_aux_lib",
    "PieceRef": "piece_ref",
    "PieceDate": "piece_date",
    "EcritureLib": "ecriture_lib",
    "Debit": "debit",
    "Credit": "credit",
    "EcrtureLet": "lettrage",
    "DateLet": "date_lettrage",
    "ValidDate": "valid_date",
    "Montantdevise": "montant_devise",
    "Idevise": "devise",
}

# Mapping type de fichier -> dictionnaire de champs
FIELD_MAPPINGS = {
    "clients": CLIENT_FIELDS,
    "fournisseurs": FOURNISSEUR_FIELDS,
    "factures_clients": FACTURE_CLIENT_FIELDS,
    "factures_fournisseurs": FACTURE_FOURNISSEUR_FIELDS,
    "commandes_clients": COMMANDE_CLIENT_FIELDS,
    "commandes_fournisseurs": COMMANDE_FOURNISSEUR_FIELDS,
    "avoirs": AVOIR_FIELDS,
    "historique": HISTORIQUE_FIELDS,
    "fec": FEC_FIELDS,
}

# Colonnes Sage qui sont des dates
DATE_FIELDS = {
    "DO_Date", "DO_DateLivr", "date_facture", "date_echeance",
    "date_commande", "date_facturation_prevue", "date_avoir", "mois",
}

# Colonnes Sage qui sont des montants
AMOUNT_FIELDS = {
    "DO_TotalHT", "DO_TotalTTC", "DO_MontantRegle",
    "MontantHT", "MontantTTC",
    "montant_ht", "montant_ttc", "montant_regle",
}
