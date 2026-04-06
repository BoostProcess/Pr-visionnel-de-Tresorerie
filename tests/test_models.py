"""Tests unitaires sur les modèles de données."""

from datetime import date

from app.models.adjustments import AjustementManuel
from app.models.assumptions import HypotheseConversion, HypotheseScenario, Saisonnalite
from app.models.cash import LignePrevisionnel, PositionTresorerie
from app.models.fixed_charges import ChargeFiscale, ChargeFix, Emprunt
from app.models.history import HistoriqueFacturation
from app.models.imports_log import ErreurImport, LotImport
from app.models.invoices import Avoir, FactureClient, FactureFournisseur
from app.models.orders import CommandeClient, CommandeFournisseur
from app.models.reference import Client, ConditionReglement, Fournisseur
from app.models.versions import VersionMensuelle


class TestModelsCreation:
    """Vérifie que chaque modèle peut être créé et lu."""

    def test_condition_reglement(self, session):
        cr = ConditionReglement(code="30NET", libelle="30 jours net", base_jours=30)
        session.add(cr)
        session.flush()
        assert cr.id is not None
        assert session.get(ConditionReglement, cr.id).code == "30NET"

    def test_client(self, session, sample_condition_30fm):
        client = Client(
            sage_code="C001", name="Test",
            condition_reglement_id=sample_condition_30fm.id,
        )
        session.add(client)
        session.flush()
        assert client.id is not None
        assert client.condition_reglement.code == "30FM"

    def test_fournisseur(self, session, sample_condition_60net):
        fournisseur = Fournisseur(
            sage_code="F001", name="Fournisseur",
            condition_reglement_id=sample_condition_60net.id,
        )
        session.add(fournisseur)
        session.flush()
        assert fournisseur.id is not None

    def test_facture_client(self, session, sample_client):
        facture = FactureClient(
            sage_doc_number="FC001", client_id=sample_client.id,
            date_facture=date(2026, 1, 15),
            montant_ht=1000000, montant_ttc=1160000,
            montant_tva=160000, reste_a_regler=1160000,
        )
        session.add(facture)
        session.flush()
        assert facture.id is not None
        assert facture.montant_ttc == 1160000

    def test_facture_fournisseur(self, session, sample_fournisseur):
        facture = FactureFournisseur(
            sage_doc_number="FF001", fournisseur_id=sample_fournisseur.id,
            date_facture=date(2026, 2, 1),
            montant_ht=500000, montant_ttc=580000,
            montant_tva=80000, reste_a_regler=580000,
        )
        session.add(facture)
        session.flush()
        assert facture.id is not None

    def test_avoir(self, session, sample_client):
        avoir = Avoir(
            sage_doc_number="AV001", type_tiers="client",
            tiers_id=sample_client.id, date_avoir=date(2026, 1, 20),
            montant_ht=50000, montant_ttc=58000,
        )
        session.add(avoir)
        session.flush()
        assert avoir.id is not None

    def test_commande_client(self, session, sample_client):
        cmd = CommandeClient(
            sage_doc_number="CC001", client_id=sample_client.id,
            date_commande=date(2026, 1, 10),
            montant_ht=2000000, montant_ttc=2320000,
            reste_a_facturer=2320000,
        )
        session.add(cmd)
        session.flush()
        assert cmd.reste_a_facturer == 2320000

    def test_commande_fournisseur(self, session, sample_fournisseur):
        cmd = CommandeFournisseur(
            sage_doc_number="CF001", fournisseur_id=sample_fournisseur.id,
            date_commande=date(2026, 2, 5),
            montant_ht=800000, montant_ttc=928000,
            reste_a_facturer=928000,
        )
        session.add(cmd)
        session.flush()
        assert cmd.id is not None

    def test_charge_fixe(self, session):
        charge = ChargeFix(
            libelle="Loyer", categorie="loyer",
            montant_ttc=450000, frequence="mensuel",
            jour_paiement=5, date_debut=date(2025, 1, 1),
        )
        session.add(charge)
        session.flush()
        assert charge.id is not None

    def test_emprunt(self, session):
        emprunt = Emprunt(
            libelle="Prêt véhicule", preteur="Banque",
            montant_initial=5000000, capital_restant=3000000,
            mensualite=120000, part_interet=20000, part_capital=100000,
            jour_paiement=10, date_debut=date(2024, 1, 1), date_fin=date(2028, 12, 31),
        )
        session.add(emprunt)
        session.flush()
        assert emprunt.mensualite == 120000

    def test_position_tresorerie(self, session):
        pos = PositionTresorerie(
            date=date(2026, 4, 1), solde_banque=15000000, est_initial=True,
        )
        session.add(pos)
        session.flush()
        assert pos.solde_banque == 15000000

    def test_version_mensuelle(self, session):
        version = VersionMensuelle(mois=date(2026, 4, 1))
        session.add(version)
        session.flush()
        assert version.est_verrouille == False

    def test_lot_import(self, session):
        lot = LotImport(
            nom_fichier="test.csv", type_fichier="clients",
            nb_lignes=10, nb_importees=8, nb_doublons=1, nb_erreurs=1,
            statut="partiel",
        )
        session.add(lot)
        session.flush()
        assert lot.id is not None

    def test_ajustement_manuel(self, session):
        adj = AjustementManuel(
            mois=date(2026, 5, 1), direction="encaissement",
            libelle="Subvention exceptionnelle",
            montant=5000000, categorie="subvention",
        )
        session.add(adj)
        session.flush()
        assert adj.montant == 5000000
