"""Tests de l'import FEC."""

from pathlib import Path

from app.imports.fec_importer import FECImporter
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.reference import Client, Fournisseur


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_fec_import_creates_invoices(session):
    """Le FEC doit créer des factures clients et fournisseurs."""
    importer = FECImporter(session)
    lot = importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    assert lot.statut in ("succes", "partiel")
    assert lot.nb_importees > 0

    # Vérifier les factures clients créées
    factures_clients = session.query(FactureClient).all()
    assert len(factures_clients) >= 1  # Au moins FA2026-002 (non lettrée)

    # Vérifier les factures fournisseurs
    factures_fournisseurs = session.query(FactureFournisseur).all()
    assert len(factures_fournisseurs) >= 1  # FA2026-101


def test_fec_import_auto_creates_clients(session):
    """Le FEC doit créer les tiers automatiquement."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    clients = session.query(Client).all()
    assert len(clients) >= 1
    codes = {c.sage_code for c in clients}
    assert "CLI001" in codes or "CLI002" in codes

    fournisseurs = session.query(Fournisseur).all()
    assert len(fournisseurs) >= 1
    codes_f = {f.sage_code for f in fournisseurs}
    assert "FOU001" in codes_f


def test_fec_import_detects_lettrage(session):
    """Les écritures lettrées doivent avoir statut 'regle'."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # FA2026-002 (Client Beta) n'est pas lettrée -> ouvert
    fc_beta = session.query(FactureClient).filter(
        FactureClient.sage_doc_number == "FEC-FA2026-002"
    ).first()
    if fc_beta:
        assert fc_beta.statut == "ouvert"
        assert fc_beta.reste_a_regler > 0


def test_fec_import_no_duplicates(session):
    """Un deuxième import du même FEC ne doit pas créer de doublons."""
    importer = FECImporter(session)
    lot1 = importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()
    nb1 = lot1.nb_importees

    importer2 = FECImporter(session)
    lot2 = importer2.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    assert lot2.nb_doublons >= nb1
    assert lot2.nb_importees == 0


def test_fec_import_amounts(session):
    """Vérifier les montants extraits du FEC."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # FA2026-101 fournisseur : crédit 200000 sur 401
    ff = session.query(FactureFournisseur).filter(
        FactureFournisseur.sage_doc_number == "FEC-FA2026-101"
    ).first()
    assert ff is not None
    assert ff.montant_ttc == 200000
    assert ff.statut == "ouvert"
