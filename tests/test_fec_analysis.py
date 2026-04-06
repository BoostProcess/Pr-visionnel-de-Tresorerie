"""Tests du service d'analyse financière FEC."""

from datetime import date

from app.models.fec_entry import EcritureFEC
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.reference import Client, Fournisseur
from app.services.fec_analysis_service import FECAnalysisService


def _seed_ecritures(session):
    """Insère des écritures FEC de test."""
    ecritures = [
        # Vente : CA 1 000 000 XPF
        EcritureFEC(
            journal_code="VE", journal_lib="Ventes", ecriture_num="001",
            ecriture_date=date(2026, 1, 15), compte_num="7010000",
            compte_lib="Ventes", piece_ref="FA001", piece_date=date(2026, 1, 15),
            ecriture_lib="Vente janvier", debit=0, credit=1000000,
        ),
        # Créance client
        EcritureFEC(
            journal_code="VE", journal_lib="Ventes", ecriture_num="001",
            ecriture_date=date(2026, 1, 15), compte_num="4110000",
            compte_lib="Clients", comp_aux_num="CLI001",
            piece_ref="FA001", piece_date=date(2026, 1, 15),
            ecriture_lib="Vente janvier", debit=1160000, credit=0,
        ),
        # TVA collectée
        EcritureFEC(
            journal_code="VE", journal_lib="Ventes", ecriture_num="001",
            ecriture_date=date(2026, 1, 15), compte_num="4457100",
            compte_lib="TVA collectée", piece_ref="FA001",
            piece_date=date(2026, 1, 15),
            ecriture_lib="TVA vente", debit=0, credit=160000,
        ),
        # Achat : 400 000 XPF
        EcritureFEC(
            journal_code="HA", journal_lib="Achats", ecriture_num="002",
            ecriture_date=date(2026, 1, 20), compte_num="6010000",
            compte_lib="Achats", piece_ref="FA101", piece_date=date(2026, 1, 20),
            ecriture_lib="Achat janvier", debit=400000, credit=0,
        ),
        # Dette fournisseur
        EcritureFEC(
            journal_code="HA", journal_lib="Achats", ecriture_num="002",
            ecriture_date=date(2026, 1, 20), compte_num="4010000",
            compte_lib="Fournisseurs", comp_aux_num="FOU001",
            piece_ref="FA101", piece_date=date(2026, 1, 20),
            ecriture_lib="Achat janvier", debit=0, credit=464000,
        ),
        # Charges personnel : 200 000 XPF
        EcritureFEC(
            journal_code="OD", journal_lib="OD Paie", ecriture_num="003",
            ecriture_date=date(2026, 1, 31), compte_num="6410000",
            compte_lib="Salaires", piece_ref="PAIE01",
            piece_date=date(2026, 1, 31),
            ecriture_lib="Salaires janvier", debit=200000, credit=0,
        ),
        # Charges externes : 50 000 XPF
        EcritureFEC(
            journal_code="HA", journal_lib="Achats", ecriture_num="004",
            ecriture_date=date(2026, 1, 25), compte_num="6130000",
            compte_lib="Loyer", piece_ref="LOY01", piece_date=date(2026, 1, 25),
            ecriture_lib="Loyer janvier", debit=50000, credit=0,
        ),
        # Dotation amortissement : 30 000 XPF
        EcritureFEC(
            journal_code="OD", journal_lib="OD", ecriture_num="005",
            ecriture_date=date(2026, 1, 31), compte_num="6811000",
            compte_lib="Dotations amortissements", piece_ref="AMORT01",
            piece_date=date(2026, 1, 31),
            ecriture_lib="Amortissement janvier", debit=30000, credit=0,
        ),
        # Trésorerie banque : 500 000 XPF (solde)
        EcritureFEC(
            journal_code="BQ", journal_lib="Banque", ecriture_num="006",
            ecriture_date=date(2026, 1, 31), compte_num="5120000",
            compte_lib="Banque", piece_ref="RG001", piece_date=date(2026, 1, 31),
            ecriture_lib="Solde banque", debit=500000, credit=0,
        ),
    ]
    for e in ecritures:
        session.add(e)
    session.flush()


def _seed_factures(session):
    """Insère des factures de test pour la balance âgée."""
    client = Client(sage_code="CLI001", name="Client Test", is_active=True)
    session.add(client)
    session.flush()

    fournisseur = Fournisseur(sage_code="FOU001", name="Fournisseur Test", is_active=True)
    session.add(fournisseur)
    session.flush()

    # Facture client ouverte (échue depuis 45 jours)
    session.add(FactureClient(
        sage_doc_number="FC001", sage_doc_type=6, client_id=client.id,
        date_facture=date(2026, 1, 1),
        date_echeance=date(2026, 2, 1),
        montant_ht=500000, montant_ttc=580000, montant_tva=80000,
        montant_regle=0, reste_a_regler=580000, statut="ouvert",
    ))

    # Facture fournisseur ouverte
    session.add(FactureFournisseur(
        sage_doc_number="FF001", sage_doc_type=6, fournisseur_id=fournisseur.id,
        date_facture=date(2026, 2, 1),
        date_echeance=date(2026, 3, 1),
        montant_ht=200000, montant_ttc=232000, montant_tva=32000,
        montant_regle=0, reste_a_regler=232000, statut="ouvert",
    ))
    session.flush()


def test_compte_resultat(session):
    """Le compte de résultat doit reconstituer les SIG."""
    _seed_ecritures(session)
    service = FECAnalysisService(session)
    cr = service.compute_compte_resultat()

    assert cr.chiffre_affaires == 1000000
    assert cr.achats == 400000
    assert cr.marge_brute == 600000
    assert cr.charges_personnel == 200000
    assert cr.charges_externes == 50000
    assert cr.dotations_amortissements == 30000
    assert cr.resultat_net > 0


def test_sig_coherence(session):
    """Les SIG doivent être cohérents entre eux."""
    _seed_ecritures(session)
    service = FECAnalysisService(session)
    cr = service.compute_compte_resultat()

    # Marge brute = CA - Achats
    assert cr.marge_brute == cr.chiffre_affaires - cr.achats

    # VA = Marge brute - Charges externes
    assert cr.valeur_ajoutee == cr.marge_brute - cr.charges_externes + cr.autres_produits

    # EBE = VA - Impôts - Personnel
    assert cr.ebe == cr.valeur_ajoutee - cr.impots_taxes - cr.charges_personnel

    # CAF = Résultat net + Dotations
    assert cr.caf == cr.resultat_net + cr.dotations_amortissements


def test_kpis(session):
    """Les KPIs doivent être calculés correctement."""
    _seed_ecritures(session)
    _seed_factures(session)
    service = FECAnalysisService(session)
    kpis = service.compute_kpis()

    assert kpis.chiffre_affaires == 1000000
    assert kpis.creances_clients == 580000
    assert kpis.dettes_fournisseurs == 232000
    assert kpis.bfr == 580000 - 232000
    assert kpis.dso_jours > 0
    assert kpis.dpo_jours > 0
    assert kpis.tresorerie_nette == 500000


def test_balance_agee_clients(session):
    """La balance âgée doit classer par ancienneté."""
    _seed_factures(session)
    service = FECAnalysisService(session)
    balance = service.compute_balance_agee_clients()

    assert len(balance) == 1
    assert balance[0].code == "CLI001"
    assert balance[0].total == 580000


def test_balance_agee_fournisseurs(session):
    """La balance âgée fournisseurs doit fonctionner."""
    _seed_factures(session)
    service = FECAnalysisService(session)
    balance = service.compute_balance_agee_fournisseurs()

    assert len(balance) == 1
    assert balance[0].code == "FOU001"
    assert balance[0].total == 232000


def test_flux_tresorerie(session):
    """Le tableau de flux de trésorerie doit être cohérent."""
    _seed_ecritures(session)
    service = FECAnalysisService(session)
    ft = service.compute_flux_tresorerie()

    # Le résultat net doit correspondre au CR
    cr = service.compute_compte_resultat()
    assert ft.resultat_net == cr.resultat_net
    assert ft.dotations_amortissements == cr.dotations_amortissements


def test_has_fec_data(session):
    """has_fec_data doit retourner True si des écritures existent."""
    service = FECAnalysisService(session)
    assert service.has_fec_data() is False

    _seed_ecritures(session)
    assert service.has_fec_data() is True
