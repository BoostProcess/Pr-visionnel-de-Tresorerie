"""Import FEC (Fichier des Écritures Comptables) depuis Sage.

Le FEC est un fichier TXT tabulé standardisé par l'administration fiscale.
Ce module extrait les factures clients et fournisseurs ouvertes à partir
des écritures comptables, en se basant sur :
- Les comptes 411xxx (créances clients)
- Les comptes 401xxx (dettes fournisseurs)
- Le lettrage pour déterminer si une écriture est soldée ou non
"""

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.config import SAGE_DATE_FORMATS, SAGE_ENCODING
from app.imports.field_mappings import FEC_FIELDS
from app.models.imports_log import ErreurImport, LotImport
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.reference import Client, Fournisseur


class FECImporter:
    """Importe un fichier FEC et en extrait les factures ouvertes."""

    # Préfixes de comptes auxiliaires
    COMPTE_CLIENT_PREFIX = "411"
    COMPTE_FOURNISSEUR_PREFIX = "401"

    def __init__(self, session: Session):
        self._session = session
        self._client_cache: dict[str, int] = {}
        self._fournisseur_cache: dict[str, int] = {}
        self._existing_docs: set[str] = set()

    def import_file(self, file_path: str, encoding: str | None = None) -> LotImport:
        """Importe un fichier FEC complet."""
        encoding = encoding or SAGE_ENCODING

        lot = LotImport(
            nom_fichier=file_path,
            type_fichier="fec",
            date_import=datetime.now(),
            statut="en_cours",
        )
        self._session.add(lot)
        self._session.flush()

        # Lire le fichier
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

        lot.nb_lignes = len(df)

        # Charger les caches
        self._build_caches()

        # Regrouper les écritures par pièce et compte auxiliaire
        ecritures_clients, ecritures_fournisseurs = self._classifier_ecritures(df, lot)

        # Créer les factures à partir des écritures regroupées
        nb_importees = 0
        nb_doublons = 0
        nb_erreurs = 0

        # Traiter les écritures clients (411xxx)
        for key, lignes in ecritures_clients.items():
            piece_ref, comp_aux = key
            result = self._creer_facture_client(piece_ref, comp_aux, lignes, lot.id)
            if result == "ok":
                nb_importees += 1
            elif result == "doublon":
                nb_doublons += 1
            else:
                nb_erreurs += 1

        # Traiter les écritures fournisseurs (401xxx)
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
        """Lit un fichier FEC (TXT tabulé ou pipe-séparé)."""
        path = Path(file_path)

        # Détecter le séparateur : TAB ou pipe
        with open(path, "r", encoding=encoding) as f:
            first_line = f.readline()

        if "\t" in first_line:
            sep = "\t"
        elif "|" in first_line:
            sep = "|"
        else:
            sep = "\t"  # Par défaut

        df = pd.read_csv(
            path,
            sep=sep,
            encoding=encoding,
            dtype=str,
            keep_default_na=False,
        )

        # Renommer les colonnes selon le mapping FEC
        rename_map = {}
        for col in df.columns:
            col_clean = col.strip()
            if col_clean in FEC_FIELDS:
                rename_map[col] = FEC_FIELDS[col_clean]
        df = df.rename(columns=rename_map)

        return df

    def _build_caches(self):
        """Pré-charge les référentiels."""
        for c in self._session.query(Client).all():
            self._client_cache[c.sage_code] = c.id
        for f in self._session.query(Fournisseur).all():
            self._fournisseur_cache[f.sage_code] = f.id

        # Cache des documents existants pour doublons
        for fc in self._session.query(FactureClient.sage_doc_number).all():
            self._existing_docs.add(fc[0])
        for ff in self._session.query(FactureFournisseur.sage_doc_number).all():
            self._existing_docs.add(ff[0])

    def _classifier_ecritures(self, df: pd.DataFrame, lot: LotImport):
        """Classe les écritures FEC en clients et fournisseurs."""
        ecritures_clients = defaultdict(list)
        ecritures_fournisseurs = defaultdict(list)

        for idx, row in df.iterrows():
            compte = str(row.get("compte_num", "")).strip()
            comp_aux = str(row.get("comp_aux_num", "")).strip()
            piece_ref = str(row.get("piece_ref", "")).strip()

            if not compte or not piece_ref:
                continue

            ligne = {
                "piece_ref": piece_ref,
                "comp_aux": comp_aux,
                "compte": compte,
                "ecriture_date": self._parse_date(row.get("ecriture_date")),
                "piece_date": self._parse_date(row.get("piece_date")),
                "ecriture_lib": str(row.get("ecriture_lib", "")).strip(),
                "debit": self._parse_amount(row.get("debit")),
                "credit": self._parse_amount(row.get("credit")),
                "lettrage": str(row.get("lettrage", "")).strip(),
                "ecriture_num": str(row.get("ecriture_num", "")).strip(),
                "journal_code": str(row.get("journal_code", "")).strip(),
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

        Retourne 'ok', 'doublon', ou 'erreur'.
        """
        doc_number = f"FEC-{piece_ref}"
        if doc_number in self._existing_docs:
            return "doublon"

        # Résoudre le client
        client_id = self._client_cache.get(comp_aux)
        if client_id is None:
            # Créer le client automatiquement
            client = Client(
                sage_code=comp_aux,
                name=lignes[0].get("ecriture_lib", comp_aux)[:100],
                is_active=True,
            )
            self._session.add(client)
            self._session.flush()
            self._client_cache[comp_aux] = client.id
            client_id = client.id

        # Calculer les montants
        # Débit sur 411 = facturation, Crédit sur 411 = règlement
        total_debit = sum(l["debit"] for l in lignes)
        total_credit = sum(l["credit"] for l in lignes)

        montant_ttc = total_debit  # Montant facturé
        montant_regle = total_credit  # Montant réglé
        reste = montant_ttc - montant_regle

        # Déterminer la date
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

        # Vérifier le lettrage : si toutes les lignes sont lettrées, c'est soldé
        toutes_lettrees = all(l["lettrage"] for l in lignes)

        statut = "regle" if toutes_lettrees or reste <= 0 else (
            "partiel" if montant_regle > 0 else "ouvert"
        )

        facture = FactureClient(
            sage_doc_number=doc_number,
            sage_doc_type=6,
            client_id=client_id,
            date_facture=date_facture,
            montant_ht=montant_ttc,  # On n'a pas le HT dans le FEC facilement
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

        Retourne 'ok', 'doublon', ou 'erreur'.
        """
        doc_number = f"FEC-{piece_ref}"
        if doc_number in self._existing_docs:
            return "doublon"

        # Résoudre le fournisseur
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

        # Crédit sur 401 = facturation, Débit sur 401 = règlement
        total_credit = sum(l["credit"] for l in lignes)
        total_debit = sum(l["debit"] for l in lignes)

        montant_ttc = total_credit
        montant_regle = total_debit
        reste = montant_ttc - montant_regle

        # Date
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

    @staticmethod
    def _parse_date(value) -> date | None:
        """Parse une date FEC."""
        if not value or str(value).strip() == "":
            return None
        if isinstance(value, (date, datetime)):
            return value if isinstance(value, date) else value.date()
        value_str = str(value).strip()
        for fmt in SAGE_DATE_FORMATS:
            try:
                return datetime.strptime(value_str, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_amount(value) -> int:
        """Parse un montant FEC en entier XPF."""
        if not value or str(value).strip() == "":
            return 0
        value_str = str(value).strip().replace(" ", "").replace("\u00a0", "")
        value_str = value_str.replace(",", ".")
        try:
            return int(round(Decimal(value_str)))
        except (InvalidOperation, ValueError):
            return 0
