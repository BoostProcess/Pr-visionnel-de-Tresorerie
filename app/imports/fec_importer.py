"""Import FEC (Fichier des Écritures Comptables) depuis Sage.

Format réglementaire défini par l'article A47 A-1 du Livre des Procédures
Fiscales (arrêté du 29 juillet 2013).

Spécifications techniques du FEC :
- Fichier TXT uniquement
- Séparateur : TAB (\\t) ou pipe (|)
- Encodage : UTF-8 ou ISO-8859-15
- Nom de fichier : SIRENFECAAAAMMJJ (date de clôture de l'exercice)
- Dates : format AAAAMMJJ sans séparateurs
- Montants : virgule comme séparateur décimal, pas de séparateur de milliers
- Écritures triées chronologiquement par EcritureNum croissant

18 colonnes obligatoires dans l'ordre :
 1. JournalCode     Alphanumérique  Obligatoire
 2. JournalLib      Alphanumérique  Obligatoire
 3. EcritureNum     Alphanumérique  Obligatoire
 4. EcritureDate    Date AAAAMMJJ   Obligatoire
 5. CompteNum       Alphanumérique  Obligatoire
 6. CompteLib       Alphanumérique  Obligatoire
 7. CompAuxNum      Alphanumérique  Facultatif (vide si pas de compte auxiliaire)
 8. CompAuxLib      Alphanumérique  Facultatif
 9. PieceRef        Alphanumérique  Obligatoire
10. PieceDate       Date AAAAMMJJ   Obligatoire
11. EcritureLib     Alphanumérique  Obligatoire
12. Debit           Numérique       Obligatoire (virgule décimale)
13. Credit          Numérique       Obligatoire (virgule décimale)
14. EcritureLet     Alphanumérique  Facultatif (code de lettrage)
15. DateLet         Date AAAAMMJJ   Facultatif (date de lettrage)
16. ValidDate       Date AAAAMMJJ   Obligatoire
17. Montantdevise   Numérique       Facultatif
18. Idevise         Alphanumérique  Facultatif

Ce module extrait les factures clients et fournisseurs ouvertes à partir
des écritures comptables, en se basant sur :
- Les comptes 411xxx (créances clients) : Débit = facture, Crédit = règlement
- Les comptes 401xxx (dettes fournisseurs) : Crédit = facture, Débit = règlement
- Le lettrage (EcritureLet) pour déterminer si une écriture est soldée ou non
"""

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models.imports_log import ErreurImport, LotImport
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.reference import Client, Fournisseur

# Noms de colonnes FEC réglementaires (dans l'ordre officiel)
FEC_COLUMNS = [
    "JournalCode",
    "JournalLib",
    "EcritureNum",
    "EcritureDate",
    "CompteNum",
    "CompteLib",
    "CompAuxNum",
    "CompAuxLib",
    "PieceRef",
    "PieceDate",
    "EcritureLib",
    "Debit",
    "Credit",
    "EcritureLet",
    "DateLet",
    "ValidDate",
    "Montantdevise",
    "Idevise",
]


class FECImporter:
    """Importe un fichier FEC réglementaire et en extrait les factures."""

    COMPTE_CLIENT_PREFIX = "411"
    COMPTE_FOURNISSEUR_PREFIX = "401"

    # Formats de date FEC : AAAAMMJJ est le format réglementaire
    # On accepte aussi JJ/MM/AAAA et AAAA-MM-JJ par tolérance
    FEC_DATE_FORMATS = ["%Y%m%d", "%d/%m/%Y", "%Y-%m-%d"]

    def __init__(self, session: Session):
        self._session = session
        self._client_cache: dict[str, int] = {}
        self._fournisseur_cache: dict[str, int] = {}
        self._existing_docs: set[str] = set()

    def import_file(self, file_path: str, encoding: str | None = None) -> LotImport:
        """Importe un fichier FEC complet.

        Args:
            file_path: chemin vers le fichier FEC (.txt)
            encoding: encodage du fichier (UTF-8 par défaut, ISO-8859-15 accepté)
        """
        encoding = encoding or "utf-8"

        lot = LotImport(
            nom_fichier=file_path,
            type_fichier="fec",
            date_import=datetime.now(),
            statut="en_cours",
        )
        self._session.add(lot)
        self._session.flush()

        # Lire le fichier FEC
        try:
            df = self._read_fec(file_path, encoding)
        except Exception as e:
            lot.statut = "echec"
            lot.nb_erreurs = 1
            self._session.add(ErreurImport(
                lot_id=lot.id, numero_ligne=0,
                type_erreur="parsing",
                message=f"Erreur de lecture du FEC : {e}",
            ))
            return lot

        # Valider la structure
        validation_errors = self._validate_structure(df)
        if validation_errors:
            for err in validation_errors:
                self._session.add(ErreurImport(
                    lot_id=lot.id, numero_ligne=0,
                    type_erreur="structure",
                    message=err,
                ))

        lot.nb_lignes = len(df)

        # Charger les caches de référence
        self._build_caches()

        # Classifier les écritures par compte (411/401) et par pièce
        ecritures_clients, ecritures_fournisseurs = self._classifier_ecritures(df, lot)

        nb_importees = 0
        nb_doublons = 0
        nb_erreurs = 0

        # Traiter les écritures clients (comptes 411xxx)
        for key, lignes in ecritures_clients.items():
            piece_ref, comp_aux = key
            result = self._creer_facture_client(piece_ref, comp_aux, lignes, lot.id)
            if result == "ok":
                nb_importees += 1
            elif result == "doublon":
                nb_doublons += 1
            else:
                nb_erreurs += 1

        # Traiter les écritures fournisseurs (comptes 401xxx)
        for key, lignes in ecritures_fournisseurs.items():
            piece_ref, comp_aux = key
            result = self._creer_facture_fournisseur(piece_ref, comp_aux, lignes, lot.id)
            if result == "ok":
                nb_importees += 1
            elif result == "doublon":
                nb_doublons += 1
            else:
                nb_erreurs += 1

        lot.nb_importees = nb_importees
        lot.nb_doublons = nb_doublons
        lot.nb_erreurs = nb_erreurs
        lot.statut = (
            "succes" if nb_erreurs == 0
            else "partiel" if nb_importees > 0
            else "echec"
        )
        return lot

    def _read_fec(self, file_path: str, encoding: str) -> pd.DataFrame:
        """Lit un fichier FEC selon le format réglementaire.

        Détecte automatiquement le séparateur (TAB ou pipe).
        """
        path = Path(file_path)

        # Détecter le séparateur en lisant la première ligne
        with open(path, "r", encoding=encoding) as f:
            first_line = f.readline()

        if "|" in first_line:
            sep = "|"
        else:
            sep = "\t"

        df = pd.read_csv(
            path,
            sep=sep,
            encoding=encoding,
            dtype=str,
            keep_default_na=False,
        )

        # Nettoyer les noms de colonnes (espaces en trop, BOM UTF-8)
        df.columns = [col.strip().lstrip("\ufeff") for col in df.columns]

        return df

    def _validate_structure(self, df: pd.DataFrame) -> list[str]:
        """Vérifie que le fichier contient bien les 18 colonnes FEC."""
        errors = []
        missing = []
        for col in FEC_COLUMNS:
            if col not in df.columns:
                missing.append(col)
        if missing:
            errors.append(
                f"Colonnes FEC manquantes : {', '.join(missing)}. "
                f"Colonnes trouvées : {', '.join(df.columns.tolist())}"
            )
        return errors

    def _build_caches(self):
        """Pré-charge les référentiels existants pour les lookups."""
        for c in self._session.query(Client).all():
            self._client_cache[c.sage_code] = c.id
        for f in self._session.query(Fournisseur).all():
            self._fournisseur_cache[f.sage_code] = f.id
        for fc in self._session.query(FactureClient.sage_doc_number).all():
            self._existing_docs.add(fc[0])
        for ff in self._session.query(FactureFournisseur.sage_doc_number).all():
            self._existing_docs.add(ff[0])

    def _classifier_ecritures(self, df: pd.DataFrame, lot: LotImport):
        """Classe les écritures FEC en clients (411) et fournisseurs (401).

        Regroupe par (PieceRef, CompAuxNum) pour reconstituer les factures.
        """
        ecritures_clients = defaultdict(list)
        ecritures_fournisseurs = defaultdict(list)

        for idx, row in df.iterrows():
            compte = str(row.get("CompteNum", "")).strip()
            comp_aux = str(row.get("CompAuxNum", "")).strip()
            piece_ref = str(row.get("PieceRef", "")).strip()

            if not compte or not piece_ref:
                continue

            ligne = {
                "piece_ref": piece_ref,
                "comp_aux": comp_aux,
                "compte": compte,
                "ecriture_date": self._parse_fec_date(row.get("EcritureDate")),
                "piece_date": self._parse_fec_date(row.get("PieceDate")),
                "ecriture_lib": str(row.get("EcritureLib", "")).strip(),
                "debit": self._parse_fec_amount(row.get("Debit")),
                "credit": self._parse_fec_amount(row.get("Credit")),
                "lettrage": str(row.get("EcritureLet", "")).strip(),
                "ecriture_num": str(row.get("EcritureNum", "")).strip(),
                "journal_code": str(row.get("JournalCode", "")).strip(),
            }

            if compte.startswith(self.COMPTE_CLIENT_PREFIX):
                key = (piece_ref, comp_aux or compte)
                ecritures_clients[key].append(ligne)
            elif compte.startswith(self.COMPTE_FOURNISSEUR_PREFIX):
                key = (piece_ref, comp_aux or compte)
                ecritures_fournisseurs[key].append(ligne)

        return ecritures_clients, ecritures_fournisseurs

    def _creer_facture_client(
        self, piece_ref: str, comp_aux: str, lignes: list[dict], lot_id: int
    ) -> str:
        """Crée une facture client à partir des écritures FEC.

        Logique comptable :
        - Débit sur 411 = montant facturé (créance)
        - Crédit sur 411 = règlement reçu
        - Si toutes les lignes sont lettrées (EcritureLet renseigné) -> soldé
        """
        doc_number = f"FEC-{piece_ref}"
        if doc_number in self._existing_docs:
            return "doublon"

        # Résoudre le client par CompAuxNum
        client_id = self._client_cache.get(comp_aux)
        if client_id is None:
            # Créer le tiers automatiquement
            client = Client(
                sage_code=comp_aux,
                name=lignes[0].get("ecriture_lib", comp_aux)[:100],
                is_active=True,
            )
            self._session.add(client)
            self._session.flush()
            self._client_cache[comp_aux] = client.id
            client_id = client.id

        # Débit 411 = facturation, Crédit 411 = règlement
        total_debit = sum(l["debit"] for l in lignes)
        total_credit = sum(l["credit"] for l in lignes)

        montant_ttc = total_debit
        montant_regle = total_credit
        reste = montant_ttc - montant_regle

        # Date de pièce (PieceDate) en priorité, sinon date d'écriture
        date_facture = None
        for l in lignes:
            if l["piece_date"]:
                date_facture = l["piece_date"]
                break
            if l["ecriture_date"]:
                date_facture = l["ecriture_date"]
                break
        if not date_facture:
            return "erreur"

        # Lettrage : si toutes les lignes ont un code lettrage -> soldé
        toutes_lettrees = all(l["lettrage"] for l in lignes)

        statut = "regle" if toutes_lettrees or reste <= 0 else (
            "partiel" if montant_regle > 0 else "ouvert"
        )

        facture = FactureClient(
            sage_doc_number=doc_number,
            sage_doc_type=6,
            client_id=client_id,
            date_facture=date_facture,
            montant_ht=montant_ttc,
            montant_ttc=montant_ttc,
            montant_tva=0,
            montant_regle=montant_regle,
            reste_a_regler=max(reste, 0),
            statut=statut,
            lot_import_id=lot_id,
        )
        self._session.add(facture)
        self._existing_docs.add(doc_number)
        return "ok"

    def _creer_facture_fournisseur(
        self, piece_ref: str, comp_aux: str, lignes: list[dict], lot_id: int
    ) -> str:
        """Crée une facture fournisseur à partir des écritures FEC.

        Logique comptable :
        - Crédit sur 401 = montant facturé (dette)
        - Débit sur 401 = règlement effectué
        """
        doc_number = f"FEC-{piece_ref}"
        if doc_number in self._existing_docs:
            return "doublon"

        fournisseur_id = self._fournisseur_cache.get(comp_aux)
        if fournisseur_id is None:
            fournisseur = Fournisseur(
                sage_code=comp_aux,
                name=lignes[0].get("ecriture_lib", comp_aux)[:100],
                is_active=True,
            )
            self._session.add(fournisseur)
            self._session.flush()
            self._fournisseur_cache[comp_aux] = fournisseur.id
            fournisseur_id = fournisseur.id

        # Crédit 401 = facturation, Débit 401 = règlement
        total_credit = sum(l["credit"] for l in lignes)
        total_debit = sum(l["debit"] for l in lignes)

        montant_ttc = total_credit
        montant_regle = total_debit
        reste = montant_ttc - montant_regle

        date_facture = None
        for l in lignes:
            if l["piece_date"]:
                date_facture = l["piece_date"]
                break
            if l["ecriture_date"]:
                date_facture = l["ecriture_date"]
                break
        if not date_facture:
            return "erreur"

        toutes_lettrees = all(l["lettrage"] for l in lignes)
        statut = "regle" if toutes_lettrees or reste <= 0 else (
            "partiel" if montant_regle > 0 else "ouvert"
        )

        facture = FactureFournisseur(
            sage_doc_number=doc_number,
            sage_doc_type=6,
            fournisseur_id=fournisseur_id,
            date_facture=date_facture,
            montant_ht=montant_ttc,
            montant_ttc=montant_ttc,
            montant_tva=0,
            montant_regle=montant_regle,
            reste_a_regler=max(reste, 0),
            statut=statut,
            lot_import_id=lot_id,
        )
        self._session.add(facture)
        self._existing_docs.add(doc_number)
        return "ok"

    @classmethod
    def _parse_fec_date(cls, value) -> date | None:
        """Parse une date FEC au format réglementaire AAAAMMJJ.

        Accepte aussi JJ/MM/AAAA et AAAA-MM-JJ par tolérance.
        """
        if not value or str(value).strip() == "":
            return None
        if isinstance(value, (date, datetime)):
            return value if isinstance(value, date) else value.date()
        value_str = str(value).strip()
        for fmt in cls.FEC_DATE_FORMATS:
            try:
                return datetime.strptime(value_str, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_fec_amount(value) -> int:
        """Parse un montant FEC en entier XPF.

        Format réglementaire : virgule comme séparateur décimal,
        pas de séparateur de milliers.
        Exemples : "500000,00" -> 500000, "1234,56" -> 1235
        """
        if not value or str(value).strip() == "":
            return 0
        value_str = str(value).strip().replace(" ", "").replace("\u00a0", "")
        # Le FEC utilise la virgule décimale (format réglementaire)
        value_str = value_str.replace(",", ".")
        try:
            return int(round(Decimal(value_str)))
        except (InvalidOperation, ValueError):
            return 0
