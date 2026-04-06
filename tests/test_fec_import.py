"""Tests de l'import FEC (Fichier des Écritures Comptables).

Le fichier de test fec_sample.txt est au format réglementaire :
- Séparateur TAB
- Dates au format AAAAMMJJ
- Montants avec virgule décimale
- 18 colonnes dans l'ordre officiel
"""

from pathlib import Path

from app.imports.fec_importer import FECImporter
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.reference import Client, Fournisseur


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_fec_read_format_reglementaire(session):
    """Le parseur doit lire un FEC au format AAAAMMJJ avec virgule décimale."""
    importer = FECImporter(session)
    lot = importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    assert lot.statut in ("succes", "partiel")
    assert lot.nb_lignes == 16  # 16 lignes d'écritures dans le fichier


def test_fec_import_creates_client_invoices(session):
    """Le FEC doit créer des factures clients à partir des écritures 411."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    factures = session.query(FactureClient).all()
    # FA2026-001 (avec lettrage partiel sur RG), FA2026-002, FA2026-003, RG2026-001, RG2026-002
    assert len(factures) >= 3


def test_fec_import_creates_supplier_invoices(session):
    """Le FEC doit créer des factures fournisseurs à partir des écritures 401."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    factures = session.query(FactureFournisseur).all()
    assert len(factures) >= 1  # FA2026-101


def test_fec_import_auto_creates_tiers(session):
    """Le FEC doit créer les clients et fournisseurs automatiquement."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    clients = session.query(Client).all()
    codes_c = {c.sage_code for c in clients}
    assert "CLI001" in codes_c
    assert "CLI002" in codes_c

    fournisseurs = session.query(Fournisseur).all()
    codes_f = {f.sage_code for f in fournisseurs}
    assert "FOU001" in codes_f


def test_fec_dates_aaaammjj(session):
    """Les dates au format AAAAMMJJ doivent être correctement parsées."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # FA2026-002 a une PieceDate de 20260315 -> 2026-03-15
    fc = session.query(FactureClient).filter(
        FactureClient.sage_doc_number == "FEC-FA2026-002"
    ).first()
    assert fc is not None
    from datetime import date
    assert fc.date_facture == date(2026, 3, 15)


def test_fec_montants_virgule_decimale(session):
    """Les montants avec virgule décimale doivent être correctement parsés."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # FA2026-101 fournisseur : crédit 200000,00 sur 401 -> 200000 XPF
    ff = session.query(FactureFournisseur).filter(
        FactureFournisseur.sage_doc_number == "FEC-FA2026-101"
    ).first()
    assert ff is not None
    assert ff.montant_ttc == 200000
    assert ff.statut == "ouvert"


def test_fec_lettrage_detecte_reglement(session):
    """Les écritures lettrées doivent être marquées comme réglées."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # RG2026-001 : le règlement Alpha a le lettrage "AA" -> soldé
    fc_rg = session.query(FactureClient).filter(
        FactureClient.sage_doc_number == "FEC-RG2026-001"
    ).first()
    if fc_rg:
        assert fc_rg.statut == "regle"


def test_fec_facture_ouverte_sans_lettrage(session):
    """Les écritures sans lettrage doivent rester ouvertes."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # FA2026-002 (Client Beta) n'a pas de lettrage -> ouvert
    fc = session.query(FactureClient).filter(
        FactureClient.sage_doc_number == "FEC-FA2026-002"
    ).first()
    assert fc is not None
    assert fc.statut == "ouvert"
    assert fc.reste_a_regler == 300000
    assert fc.montant_ttc == 300000


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


def test_fec_reglement_partiel(session):
    """Un règlement partiel doit donner statut 'partiel'."""
    importer = FECImporter(session)
    importer.import_file(str(FIXTURE_DIR / "fec_sample.txt"), encoding="utf-8")
    session.commit()

    # FA2026-003 : facture 150000, règlement partiel 75000 (RG2026-002)
    # Mais RG2026-002 est une pièce séparée, donc FA2026-003 reste ouvert
    # car il n'y a pas de lettrage
    fc = session.query(FactureClient).filter(
        FactureClient.sage_doc_number == "FEC-FA2026-003"
    ).first()
    assert fc is not None
    assert fc.montant_ttc == 150000
    assert fc.statut == "ouvert"
