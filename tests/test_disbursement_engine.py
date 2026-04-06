"""Tests du moteur de décaissements."""

from datetime import date

from app.calculations.disbursement_engine import DisbursementEngine
from app.models.invoices import Avoir, FactureFournisseur
from app.models.orders import CommandeFournisseur
from app.models.reference import ConditionReglement, Fournisseur


class TestDisbursementEngine:
    """Tests des décaissements."""

    def setup_method(self):
        self.engine = DisbursementEngine()

    def _setup_basic_data(self, session):
        cr = ConditionReglement(
            code="60NET", libelle="60 jours net",
            base_jours=60, fin_de_mois=False,
        )
        session.add(cr)
        session.flush()

        fournisseur = Fournisseur(
            sage_code="FRN001", name="Fournisseur A",
            condition_reglement_id=cr.id,
        )
        session.add(fournisseur)
        session.flush()
        return cr, fournisseur

    def test_open_supplier_invoice(self, session):
        """Facture fournisseur ouverte -> décaissement."""
        cr, fournisseur = self._setup_basic_data(session)

        facture = FactureFournisseur(
            sage_doc_number="FF001", fournisseur_id=fournisseur.id,
            date_facture=date(2026, 1, 10),
            date_echeance=date(2026, 3, 11),
            montant_ht=800000, montant_ttc=928000,
            montant_tva=128000, reste_a_regler=928000,
            statut="ouvert",
        )
        session.add(facture)
        session.flush()

        lines = self.engine.compute_disbursements(
            session, "central", date(2026, 1, 1), 6,
        )

        assert len(lines) == 1
        assert lines[0].montant == -928000  # Négatif = décaissement
        assert lines[0].mois == date(2026, 3, 1)

    def test_supplier_order_conversion(self, session):
        """Commande fournisseur -> décaissement prévisionnel."""
        cr, fournisseur = self._setup_basic_data(session)

        commande = CommandeFournisseur(
            sage_doc_number="CF001", fournisseur_id=fournisseur.id,
            date_commande=date(2026, 2, 1),
            montant_ht=1500000, montant_ttc=1740000,
            reste_a_facturer=1740000, statut="ouverte",
        )
        session.add(commande)
        session.flush()

        lines = self.engine.compute_disbursements(
            session, "central", date(2026, 1, 1), 12,
            conversion_delay=30, confidence_pct=0.95,
        )

        cmd_lines = [l for l in lines if l.categorie == "decaissement_commande"]
        assert len(cmd_lines) == 1
        assert cmd_lines[0].montant == -int(1740000 * 0.95)

    def test_supplier_credit_note(self, session):
        """Avoir fournisseur réduit les décaissements."""
        cr, fournisseur = self._setup_basic_data(session)

        avoir = Avoir(
            sage_doc_number="AVF001", type_tiers="fournisseur",
            tiers_id=fournisseur.id, date_avoir=date(2026, 3, 10),
            montant_ht=200000, montant_ttc=232000,
        )
        session.add(avoir)
        session.flush()

        lines = self.engine.compute_disbursements(
            session, "central", date(2026, 1, 1), 6,
        )

        avoir_lines = [l for l in lines if l.categorie == "avoir_fournisseur"]
        assert len(avoir_lines) == 1
        assert avoir_lines[0].montant == 232000  # Positif = réduit les décaissements

    def test_partial_supplier_payment(self, session):
        """Facture fournisseur partiellement réglée."""
        cr, fournisseur = self._setup_basic_data(session)

        facture = FactureFournisseur(
            sage_doc_number="FF002", fournisseur_id=fournisseur.id,
            date_facture=date(2026, 1, 5),
            date_echeance=date(2026, 3, 6),
            montant_ht=600000, montant_ttc=696000,
            montant_tva=96000, montant_regle=200000,
            reste_a_regler=496000, statut="partiel",
        )
        session.add(facture)
        session.flush()

        lines = self.engine.compute_disbursements(
            session, "central", date(2026, 1, 1), 6,
        )

        assert len(lines) == 1
        assert lines[0].montant == -496000
