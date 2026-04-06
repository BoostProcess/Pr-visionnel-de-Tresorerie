"""Tests du moteur d'encaissements."""

from datetime import date

import pytest

from app.calculations.collection_engine import CollectionEngine
from app.models.cash import PositionTresorerie
from app.models.invoices import Avoir, FactureClient
from app.models.orders import CommandeClient
from app.models.reference import Client, ConditionReglement


class TestCollectionEngine:
    """Tests des encaissements."""

    def setup_method(self):
        self.engine = CollectionEngine()

    def _setup_basic_data(self, session):
        """Crée des données de base pour les tests."""
        cr = ConditionReglement(
            code="30FM", libelle="30 jours fin de mois",
            base_jours=30, fin_de_mois=True,
        )
        session.add(cr)
        session.flush()

        client = Client(
            sage_code="CLI001", name="Client A",
            condition_reglement_id=cr.id,
        )
        session.add(client)
        session.flush()
        return cr, client

    def test_open_invoice_collection(self, session):
        """Facture ouverte -> encaissement au mois d'échéance."""
        cr, client = self._setup_basic_data(session)

        facture = FactureClient(
            sage_doc_number="FC001", client_id=client.id,
            date_facture=date(2026, 1, 15),
            date_echeance=date(2026, 2, 28),
            montant_ht=1000000, montant_ttc=1160000,
            montant_tva=160000, montant_regle=0,
            reste_a_regler=1160000, statut="ouvert",
        )
        session.add(facture)
        session.flush()

        lines = self.engine.compute_collections(
            session, "central", date(2026, 1, 1), 6,
        )

        assert len(lines) == 1
        assert lines[0].montant == 1160000
        assert lines[0].mois == date(2026, 2, 1)

    def test_partial_payment(self, session):
        """Facture partiellement réglée -> encaissement du reste."""
        cr, client = self._setup_basic_data(session)

        facture = FactureClient(
            sage_doc_number="FC002", client_id=client.id,
            date_facture=date(2026, 1, 10),
            date_echeance=date(2026, 2, 28),
            montant_ht=1000000, montant_ttc=1160000,
            montant_tva=160000, montant_regle=400000,
            reste_a_regler=760000, statut="partiel",
        )
        session.add(facture)
        session.flush()

        lines = self.engine.compute_collections(
            session, "central", date(2026, 1, 1), 6,
        )

        assert len(lines) == 1
        assert lines[0].montant == 760000

    def test_disputed_invoice_prudent(self, session):
        """Facture en litige exclue en scénario prudent."""
        cr, client = self._setup_basic_data(session)

        facture = FactureClient(
            sage_doc_number="FC003", client_id=client.id,
            date_facture=date(2026, 1, 15),
            date_echeance=date(2026, 2, 28),
            montant_ht=500000, montant_ttc=580000,
            montant_tva=80000, reste_a_regler=580000,
            statut="ouvert", en_litige=True,
        )
        session.add(facture)
        session.flush()

        lines = self.engine.compute_collections(
            session, "prudent", date(2026, 1, 1), 6,
        )
        assert len(lines) == 0

    def test_disputed_invoice_central(self, session):
        """Facture en litige : 50% en scénario central."""
        cr, client = self._setup_basic_data(session)

        facture = FactureClient(
            sage_doc_number="FC004", client_id=client.id,
            date_facture=date(2026, 1, 15),
            date_echeance=date(2026, 2, 28),
            montant_ht=500000, montant_ttc=580000,
            montant_tva=80000, reste_a_regler=580000,
            statut="ouvert", en_litige=True,
        )
        session.add(facture)
        session.flush()

        lines = self.engine.compute_collections(
            session, "central", date(2026, 1, 1), 6,
        )
        assert len(lines) == 1
        assert lines[0].montant == 290000  # 580000 / 2

    def test_credit_note_reduces_collection(self, session):
        """Avoir client réduit les encaissements."""
        cr, client = self._setup_basic_data(session)

        avoir = Avoir(
            sage_doc_number="AV001", type_tiers="client",
            tiers_id=client.id, date_avoir=date(2026, 3, 15),
            montant_ht=100000, montant_ttc=116000,
        )
        session.add(avoir)
        session.flush()

        lines = self.engine.compute_collections(
            session, "central", date(2026, 1, 1), 6,
        )

        avoir_lines = [l for l in lines if l.categorie == "avoir_client"]
        assert len(avoir_lines) == 1
        assert avoir_lines[0].montant == -116000  # Négatif

    def test_client_order_conversion(self, session):
        """Commande client non facturée -> encaissement prévisionnel."""
        cr, client = self._setup_basic_data(session)

        commande = CommandeClient(
            sage_doc_number="CC001", client_id=client.id,
            date_commande=date(2026, 1, 5),
            montant_ht=2000000, montant_ttc=2320000,
            montant_facture=0, reste_a_facturer=2320000,
            statut="ouverte",
        )
        session.add(commande)
        session.flush()

        lines = self.engine.compute_collections(
            session, "central", date(2026, 1, 1), 12,
            conversion_delay=30, confidence_pct=0.90,
        )

        cmd_lines = [l for l in lines if l.categorie == "encaissement_commande"]
        assert len(cmd_lines) == 1
        assert cmd_lines[0].montant == int(2320000 * 0.90)

    def test_late_payment_scenario(self, session):
        """Scénario prudent : retard de 15 jours."""
        cr, client = self._setup_basic_data(session)

        facture = FactureClient(
            sage_doc_number="FC005", client_id=client.id,
            date_facture=date(2026, 1, 15),
            date_echeance=date(2026, 2, 28),
            montant_ht=1000000, montant_ttc=1160000,
            montant_tva=160000, reste_a_regler=1160000,
            statut="ouvert",
        )
        session.add(facture)
        session.flush()

        # Central : encaissement en février
        central_lines = self.engine.compute_collections(
            session, "central", date(2026, 1, 1), 6, late_days=0,
        )
        assert central_lines[0].mois == date(2026, 2, 1)

        # Prudent : +15 jours -> encaissement en mars
        prudent_lines = self.engine.compute_collections(
            session, "prudent", date(2026, 1, 1), 6, late_days=15,
        )
        assert prudent_lines[0].mois == date(2026, 3, 1)
