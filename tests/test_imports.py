"""Tests du moteur d'import."""

from pathlib import Path

import pytest

from app.imports.import_service import ImportService
from app.imports.parsers import SageFileParser
from app.models.reference import Client, ConditionReglement, Fournisseur
from app.models.invoices import FactureClient

FIXTURES = Path(__file__).parent / "fixtures"


class TestSageFileParser:
    """Tests du parseur de fichiers Sage."""

    def test_parse_clients_csv(self):
        parser = SageFileParser(str(FIXTURES / "clients.csv"), "clients", encoding="utf-8")
        rows = parser.parse()
        assert len(rows) == 5
        assert rows[0]["sage_code"] == "CLI001"
        assert rows[0]["name"] == "Hotel Maeva"

    def test_parse_factures_csv(self):
        parser = SageFileParser(
            str(FIXTURES / "factures_clients.csv"), "factures_clients", encoding="utf-8",
        )
        rows = parser.parse()
        assert len(rows) == 5
        assert rows[0]["sage_doc_number"] == "FC2026-001"
        assert rows[0]["montant_ttc"] == 3480000

    def test_parse_amount_with_comma(self):
        """Les montants avec virgule décimale sont bien parsés."""
        result = SageFileParser._parse_amount("1 500 000,50")
        assert result == 1500000 or result == 1500001  # Arrondi XPF (banker's rounding)
        # Montant entier
        result2 = SageFileParser._parse_amount("1 500 000")
        assert result2 == 1500000

    def test_parse_date_formats(self):
        """Différents formats de date sont supportés."""
        from datetime import date
        assert SageFileParser._parse_date("15/01/2026") == date(2026, 1, 15)
        assert SageFileParser._parse_date("20260115") == date(2026, 1, 15)
        assert SageFileParser._parse_date("2026-01-15") == date(2026, 1, 15)


class TestImportService:
    """Tests d'intégration du service d'import."""

    def test_import_clients(self, session):
        """Import de clients depuis CSV."""
        # Créer les conditions de règlement référencées
        for code in ["30FM", "45FM10", "60NET"]:
            session.add(ConditionReglement(code=code, libelle=code, base_jours=30))
        session.flush()

        service = ImportService(session)
        lot = service.import_file(str(FIXTURES / "clients.csv"), "clients", encoding="utf-8")

        assert lot.nb_importees == 5
        assert lot.nb_erreurs == 0
        assert lot.statut == "succes"

        clients = session.query(Client).all()
        assert len(clients) == 5

    def test_import_duplicates_detected(self, session):
        """Les doublons sont détectés au 2ème import."""
        for code in ["30FM", "45FM10", "60NET"]:
            session.add(ConditionReglement(code=code, libelle=code, base_jours=30))
        session.flush()

        service = ImportService(session)

        # Premier import
        lot1 = service.import_file(str(FIXTURES / "clients.csv"), "clients", encoding="utf-8")
        assert lot1.nb_importees == 5

        # Deuxième import du même fichier
        lot2 = service.import_file(str(FIXTURES / "clients.csv"), "clients", encoding="utf-8")
        assert lot2.nb_importees == 0
        assert lot2.nb_doublons == 5

    def test_import_factures_with_references(self, session):
        """Import de factures après les clients."""
        # D'abord les conditions de règlement
        for code in ["30FM", "45FM10", "60NET"]:
            session.add(ConditionReglement(code=code, libelle=code, base_jours=30))
        session.flush()

        service = ImportService(session)

        # Importer les clients d'abord
        service.import_file(str(FIXTURES / "clients.csv"), "clients", encoding="utf-8")
        session.flush()

        # Puis les factures
        lot = service.import_file(
            str(FIXTURES / "factures_clients.csv"), "factures_clients", encoding="utf-8",
        )

        assert lot.nb_importees == 5
        factures = session.query(FactureClient).all()
        assert len(factures) == 5

        # Vérifier le statut calculé
        fc_paid = session.query(FactureClient).filter(
            FactureClient.sage_doc_number == "FC2026-005"
        ).first()
        assert fc_paid.statut == "regle"  # Entièrement payée

        fc_partial = session.query(FactureClient).filter(
            FactureClient.sage_doc_number == "FC2026-003"
        ).first()
        assert fc_partial.statut == "partiel"

    def test_import_multiple_files_ordered(self, session):
        """Import multi-fichiers dans le bon ordre."""
        for code in ["30FM", "45FM10", "60NET"]:
            session.add(ConditionReglement(code=code, libelle=code, base_jours=30))
        session.flush()

        service = ImportService(session)
        files = [
            (str(FIXTURES / "factures_clients.csv"), "factures_clients"),
            (str(FIXTURES / "clients.csv"), "clients"),
        ]

        # Même si les factures sont en premier dans la liste,
        # le service doit importer les clients d'abord
        lots = service.import_multiple(files)
        assert lots[0].type_fichier == "clients"
        assert lots[1].type_fichier == "factures_clients"
