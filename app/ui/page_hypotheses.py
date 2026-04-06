"""Page 4 : Hypothèses et paramètres de scénarios."""

import streamlit as st

from app.models.assumptions import HypotheseConversion, HypotheseScenario, Saisonnalite
from app.services.forecast_service import ForecastService
from app.services.referentiel_service import ReferentielService
from app.ui.components.filters import MOIS_FR, format_xpf
from app.config import SCENARIO_ADJUSTMENTS, TVA_RATES


def render(session, run_forecast_callback=None):
    """Affiche et permet de modifier les hypothèses."""
    st.header("Hypothèses et paramètres")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Scénarios", "Saisonnalité", "TVA / Taxes", "Trésorerie initiale"
    ])

    with tab1:
        _render_scenarios(session)

    with tab2:
        _render_seasonality(session)

    with tab3:
        _render_tax_params()

    with tab4:
        _render_initial_cash(session)

    st.divider()

    # Bouton recalcul
    if st.button("Recalculer le prévisionnel", type="primary", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            service = ForecastService(session)
            results = service.recalculate()
            session.commit()
            st.success(f"Prévisionnel recalculé : {sum(len(v) for v in results.values())} mois calculés.")
            if run_forecast_callback:
                run_forecast_callback(results)


def _render_scenarios(session):
    """Affiche les paramètres de scénarios."""
    st.subheader("Paramètres des scénarios")

    for scenario, params in SCENARIO_ADJUSTMENTS.items():
        with st.expander(f"Scénario {scenario.capitalize()}", expanded=(scenario == "central")):
            st.write(f"**Retard clients** : {params['retard_client_jours']:+d} jours")
            st.write(f"**Ajustement conversion commandes** : {params['taux_conversion_commandes']:+.0%}")
            st.write(f"**Décalage fournisseurs** : {params['avance_fournisseur_jours']:+d} jours")

    # Hypothèses de conversion
    st.subheader("Conversion commandes → factures")
    conversion = session.query(HypotheseConversion).first()
    with st.form("conversion_form"):
        delai = st.number_input(
            "Délai moyen de facturation (jours)",
            value=conversion.delai_moyen_facturation if conversion else 30,
            min_value=0,
            max_value=365,
        )
        confiance = st.number_input(
            "Taux de confiance (%)",
            value=float(conversion.taux_confiance) if conversion else 90.0,
            min_value=0.0,
            max_value=100.0,
            step=5.0,
        )
        if st.form_submit_button("Enregistrer"):
            if conversion:
                conversion.delai_moyen_facturation = delai
                conversion.taux_confiance = confiance
            else:
                session.add(HypotheseConversion(
                    type_commande="client",
                    delai_moyen_facturation=delai,
                    taux_confiance=confiance,
                ))
            session.flush()
            st.success("Hypothèse de conversion enregistrée.")


def _render_seasonality(session):
    """Affiche et modifie les facteurs de saisonnalité."""
    st.subheader("Saisonnalité (facteurs mensuels)")
    st.caption("1.0 = mois normal, 0.7 = basse saison, 1.3 = haute saison")

    existing = {s.numero_mois: s for s in session.query(Saisonnalite).all()}

    with st.form("seasonality_form"):
        cols = st.columns(4)
        values = {}
        for i in range(12):
            with cols[i % 4]:
                current = float(existing[i + 1].facteur) if (i + 1) in existing else 1.0
                values[i + 1] = st.number_input(
                    MOIS_FR[i],
                    value=current,
                    min_value=0.0,
                    max_value=3.0,
                    step=0.05,
                    key=f"season_{i}",
                )

        if st.form_submit_button("Enregistrer"):
            for month_num, factor in values.items():
                if month_num in existing:
                    existing[month_num].facteur = factor
                else:
                    session.add(Saisonnalite(numero_mois=month_num, facteur=factor))
            session.flush()
            st.success("Saisonnalité enregistrée.")


def _render_tax_params():
    """Affiche les paramètres TVA."""
    st.subheader("TVA Polynésie Française")
    for rate_name, rate_value in TVA_RATES.items():
        st.write(f"- **{rate_name.capitalize()}** : {rate_value:.0%}")
    st.info("Le calcul utilise le taux normal (16%) par défaut. "
            "La TVA est décaissée le mois M+1 (régime mensuel).")


def _render_initial_cash(session):
    """Permet de définir la trésorerie initiale."""
    st.subheader("Trésorerie de départ")

    service = ReferentielService(session)
    current = service.get_initial_cash()

    with st.form("initial_cash_form"):
        solde = st.number_input(
            "Solde bancaire initial (F)",
            value=current.solde_banque if current else 0,
            step=100000,
        )
        dt = st.date_input(
            "Date",
            value=current.date if current else None,
        )
        if st.form_submit_button("Enregistrer"):
            service.set_initial_cash(solde, dt)
            session.flush()
            st.success(f"Trésorerie initiale : {format_xpf(solde)}")
