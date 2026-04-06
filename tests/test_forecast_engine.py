"""Tests d'intégration du moteur de prévisionnel."""

from datetime import date

from app.calculations.forecast_engine import ForecastEngine
from app.models.cash import PositionTresorerie
from app.models.fixed_charges import ChargeFix, Emprunt
from app.models.invoices import FactureClient, FactureFournisseur
from app.models.orders import CommandeClient
from app.models.reference import Client, ConditionReglement, Fournisseur


class TestForecastEngine:
    """Tests d'intégration du prévisionnel complet."""

    def _seed_data(self, session):
        """Crée un jeu de données de test réaliste."""
        # Conditions de règlement
        cr_30fm = ConditionReglement(
            code="30FM", libelle="30 jours fin de mois",
            base_jours=30, fin_de_mois=True,
        )
        cr_60net = ConditionReglement(
            code="60NET", libelle="60 jours net",
            base_jours=60, fin_de_mois=False,
        )
        session.add_all([cr_30fm, cr_60net])
        session.flush()

        # Clients
        client1 = Client(sage_code="CLI001", name="Hotel Maeva", condition_reglement_id=cr_30fm.id)
        client2 = Client(sage_code="CLI002", name="Resort Bora", condition_reglement_id=cr_30fm.id)
        session.add_all([client1, client2])
        session.flush()

        # Fournisseur
        fournisseur = Fournisseur(sage_code="FRN001", name="Matériaux PF", condition_reglement_id=cr_60net.id)
        session.add(fournisseur)
        session.flush()

        # Trésorerie initiale
        session.add(PositionTresorerie(date=date(2026, 4, 1), solde_banque=15000000, est_initial=True))

        # Factures clients ouvertes
        session.add(FactureClient(
            sage_doc_number="FC001", client_id=client1.id,
            date_facture=date(2026, 3, 15), date_echeance=date(2026, 4, 30),
            montant_ht=3000000, montant_ttc=3480000, montant_tva=480000,
            reste_a_regler=3480000, statut="ouvert",
        ))
        session.add(FactureClient(
            sage_doc_number="FC002", client_id=client2.id,
            date_facture=date(2026, 3, 20),
            montant_ht=2000000, montant_ttc=2320000, montant_tva=320000,
            reste_a_regler=2320000, statut="ouvert",
        ))

        # Facture fournisseur ouverte
        session.add(FactureFournisseur(
            sage_doc_number="FF001", fournisseur_id=fournisseur.id,
            date_facture=date(2026, 3, 1), date_echeance=date(2026, 5, 1),
            montant_ht=1500000, montant_ttc=1740000, montant_tva=240000,
            reste_a_regler=1740000, statut="ouvert",
        ))

        # Commande client
        session.add(CommandeClient(
            sage_doc_number="CC001", client_id=client1.id,
            date_commande=date(2026, 3, 25),
            montant_ht=5000000, montant_ttc=5800000,
            reste_a_facturer=5800000, statut="ouverte",
        ))

        # Charge fixe
        session.add(ChargeFix(
            libelle="Loyer", categorie="loyer",
            montant_ttc=450000, frequence="mensuel",
            jour_paiement=5, date_debut=date(2025, 1, 1),
        ))

        # Emprunt
        session.add(Emprunt(
            libelle="Prêt équipement", preteur="Banque de Polynésie",
            montant_initial=10000000, capital_restant=6000000,
            mensualite=180000, part_interet=30000, part_capital=150000,
            jour_paiement=10, date_debut=date(2024, 1, 1), date_fin=date(2029, 12, 31),
        ))

        session.flush()

    def test_forecast_produces_3_scenarios(self, session):
        """Le prévisionnel produit des résultats pour les 3 scénarios."""
        self._seed_data(session)
        engine = ForecastEngine(session)
        results = engine.run_forecast(date(2026, 4, 1), months=6)

        assert "prudent" in results
        assert "central" in results
        assert "ambitieux" in results
        assert len(results["central"]) > 0

    def test_cash_flow_continuity(self, session):
        """Trésorerie fin M == trésorerie début M+1."""
        self._seed_data(session)
        engine = ForecastEngine(session)
        results = engine.run_forecast(date(2026, 4, 1), months=6)

        for scenario, summaries in results.items():
            for i in range(len(summaries) - 1):
                assert summaries[i].tresorerie_fin == summaries[i + 1].tresorerie_debut, (
                    f"Rupture de continuité {scenario} entre "
                    f"{summaries[i].mois} et {summaries[i+1].mois}: "
                    f"{summaries[i].tresorerie_fin} != {summaries[i+1].tresorerie_debut}"
                )

    def test_initial_cash_is_used(self, session):
        """La trésorerie initiale est bien prise en compte."""
        self._seed_data(session)
        engine = ForecastEngine(session)
        results = engine.run_forecast(date(2026, 4, 1), months=3)

        first_month = results["central"][0]
        assert first_month.tresorerie_debut == 15000000

    def test_prudent_vs_ambitieux(self, session):
        """Le scénario prudent produit une trésorerie inférieure à l'ambitieux."""
        self._seed_data(session)
        engine = ForecastEngine(session)
        results = engine.run_forecast(date(2026, 4, 1), months=6)

        prudent_final = results["prudent"][-1].tresorerie_fin
        ambitieux_final = results["ambitieux"][-1].tresorerie_fin
        assert prudent_final <= ambitieux_final, (
            f"Prudent ({prudent_final}) devrait être <= Ambitieux ({ambitieux_final})"
        )

    def test_fixed_charges_monthly(self, session):
        """Les charges fixes mensuelles apparaissent chaque mois."""
        self._seed_data(session)
        engine = ForecastEngine(session)
        results = engine.run_forecast(date(2026, 4, 1), months=3)

        # Chaque mois doit avoir des charges fixes
        for summary in results["central"]:
            assert summary.charges_fixes < 0, (
                f"Charges fixes manquantes pour {summary.mois}"
            )

    def test_recalculate(self, session):
        """Le recalcul produit des résultats cohérents."""
        self._seed_data(session)
        engine = ForecastEngine(session)

        # Premier calcul
        results1 = engine.run_forecast(date(2026, 4, 1), months=6)

        # Recalcul (uses default months=24, so compare first months only)
        results2 = engine.recalculate()

        # Les premiers mois doivent avoir la même trésorerie initiale
        for scenario in ["prudent", "central", "ambitieux"]:
            assert results2[scenario][0].tresorerie_debut == 15000000
            # La continuité doit être respectée dans le recalcul
            for i in range(len(results2[scenario]) - 1):
                assert results2[scenario][i].tresorerie_fin == results2[scenario][i + 1].tresorerie_debut
