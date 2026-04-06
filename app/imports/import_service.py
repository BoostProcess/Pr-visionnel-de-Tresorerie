"""Service d'orchestration des imports Sage."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.imports.anomaly_detector import AnomalyDetector
from app.imports.duplicate_detector import DuplicateDetector
from app.imports.loaders import DataLoader
from app.imports.parsers import SageFileParser
from app.imports.validators import RowValidator
from app.models.imports_log import ErreurImport, LotImport


# Ordre d'import obligatoire (les référentiels avant les documents)
IMPORT_ORDER = [
    "clients",
    "fournisseurs",
    "factures_clients",
    "factures_fournisseurs",
    "commandes_clients",
    "commandes_fournisseurs",
    "avoirs",
    "historique",
    "fec",
]


class ImportService:
    """Orchestre l'import complet d'un fichier Sage."""

    def __init__(self, session: Session):
        self._session = session
        self._validator = RowValidator()
        self._anomaly_detector = AnomalyDetector()
        self._duplicate_detector = DuplicateDetector(session)
        self._loader = DataLoader(session)

    def import_file(
        self, file_path: str, file_type: str, encoding: str | None = None
    ) -> LotImport:
        """Importe un fichier complet. Retourne le lot d'import."""
        # Import FEC : traitement spécifique
        if file_type == "fec":
            from app.imports.fec_importer import FECImporter
            fec = FECImporter(self._session)
            return fec.import_file(file_path, encoding)

        # Créer le lot d'import
        lot = LotImport(
            nom_fichier=file_path,
            type_fichier=file_type,
            date_import=datetime.now(),
            statut="en_cours",
        )
        self._session.add(lot)
        self._session.flush()

        # Parser le fichier
        parser = SageFileParser(file_path, file_type, encoding)
        try:
            rows = parser.parse()
        except Exception as e:
            lot.statut = "echec"
            lot.nb_erreurs = 1
            self._session.add(
                ErreurImport(
                    lot_id=lot.id,
                    numero_ligne=0,
                    type_erreur="parsing",
                    message=f"Erreur de lecture du fichier : {e}",
                )
            )
            return lot

        lot.nb_lignes = len(rows)

        # Préparer les caches
        self._duplicate_detector.build_cache(file_type)
        self._loader.build_reference_caches()

        key_field = DuplicateDetector.get_key_field(file_type)
        nb_importees = 0
        nb_doublons = 0
        nb_erreurs = 0

        for i, row in enumerate(rows, start=1):
            # 1. Valider
            errors = self._validator.validate(row, file_type)
            if errors:
                for err in errors:
                    self._session.add(
                        ErreurImport(
                            lot_id=lot.id,
                            numero_ligne=i,
                            type_erreur="validation",
                            message=err,
                        )
                    )
                nb_erreurs += 1
                continue

            # 2. Détecter les doublons
            key_value = row.get(key_field, "")
            if key_value and self._duplicate_detector.is_duplicate(file_type, key_value):
                self._session.add(
                    ErreurImport(
                        lot_id=lot.id,
                        numero_ligne=i,
                        type_erreur="doublon",
                        valeur_brute=key_value,
                        message=f"Doublon détecté : {key_field}={key_value}",
                    )
                )
                nb_doublons += 1
                continue

            # 3. Détecter les anomalies (non-bloquant)
            anomalies = self._anomaly_detector.detect(row, file_type)
            for anomaly in anomalies:
                self._session.add(
                    ErreurImport(
                        lot_id=lot.id,
                        numero_ligne=i,
                        type_erreur="anomalie",
                        message=anomaly,
                    )
                )

            # 4. Charger en base
            try:
                success = self._loader.load_row(row, file_type, lot.id)
                if success:
                    nb_importees += 1
                    if key_value:
                        self._duplicate_detector.add_to_cache(file_type, key_value)
                else:
                    nb_erreurs += 1
                    self._session.add(
                        ErreurImport(
                            lot_id=lot.id,
                            numero_ligne=i,
                            type_erreur="chargement",
                            message="Impossible de charger la ligne (référence manquante ?)",
                        )
                    )
            except Exception as e:
                nb_erreurs += 1
                self._session.add(
                    ErreurImport(
                        lot_id=lot.id,
                        numero_ligne=i,
                        type_erreur="chargement",
                        message=str(e),
                    )
                )

        # Mettre à jour le lot
        lot.nb_importees = nb_importees
        lot.nb_doublons = nb_doublons
        lot.nb_erreurs = nb_erreurs
        lot.statut = "succes" if nb_erreurs == 0 else "partiel" if nb_importees > 0 else "echec"

        return lot

    def import_multiple(self, files: list[tuple[str, str]]) -> list[LotImport]:
        """Importe plusieurs fichiers dans l'ordre correct.

        Args:
            files: liste de (chemin_fichier, type_fichier)

        Returns:
            Liste de LotImport créés.
        """
        # Trier selon l'ordre d'import
        sorted_files = sorted(
            files,
            key=lambda f: IMPORT_ORDER.index(f[1]) if f[1] in IMPORT_ORDER else 99,
        )
        results = []
        for file_path, file_type in sorted_files:
            lot = self.import_file(file_path, file_type)
            results.append(lot)
        return results
