"""Point d'entrée de l'application Streamlit - Prévisionnel de Trésorerie."""

import sys
from pathlib import Path

# Ajouter la racine du projet au path pour que les imports 'app.*' fonctionnent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.models.database import get_session, init_db

# Initialiser la base de données
init_db()

st.set_page_config(
    page_title="Prévisionnel de Trésorerie",
    page_icon="F",
    layout="wide",
)

# Navigation sidebar
PAGES = {
    "Synthèse": "dashboard",
    "Analyse financière": "analyse_fec",
    "Balance âgée": "balance_agee",
    "Encaissements": "encaissements",
    "Décaissements": "decaissements",
    "Hypothèses": "hypotheses",
    "Référentiels": "referentiels",
    "Imports": "imports",
    "Ajustements": "ajustements",
}

st.sidebar.title("Prévisionnel de Trésorerie")
st.sidebar.caption("Devise : XPF (Franc Pacifique)")
page = st.sidebar.radio("Navigation", list(PAGES.keys()))

# Session DB partagée
with get_session() as session:
    if PAGES[page] == "dashboard":
        from app.ui.page_dashboard import render as render_dashboard
        from app.services.forecast_service import ForecastService

        service = ForecastService(session)

        # Charger ou calculer les données
        if "forecast_data" not in st.session_state:
            if service.has_forecast_data():
                # Recalculer à partir des données existantes
                st.session_state["forecast_data"] = service.run_forecast()
                session.commit()
            else:
                st.session_state["forecast_data"] = {}

        render_dashboard(st.session_state.get("forecast_data", {}))

    elif PAGES[page] == "analyse_fec":
        from app.ui.page_analyse_fec import render as render_analyse
        render_analyse(session)

    elif PAGES[page] == "balance_agee":
        from app.ui.page_balance_agee import render as render_balance
        render_balance(session)

    elif PAGES[page] == "encaissements":
        from app.ui.page_encaissements import render as render_enc
        render_enc(session)

    elif PAGES[page] == "decaissements":
        from app.ui.page_decaissements import render as render_dec
        render_dec(session)

    elif PAGES[page] == "hypotheses":
        from app.ui.page_hypotheses import render as render_hyp

        def on_forecast_done(results):
            st.session_state["forecast_data"] = results

        render_hyp(session, run_forecast_callback=on_forecast_done)

    elif PAGES[page] == "referentiels":
        from app.ui.page_referentiels import render as render_ref
        render_ref(session)

    elif PAGES[page] == "imports":
        from app.ui.page_imports import render as render_imp
        render_imp(session)

    elif PAGES[page] == "ajustements":
        from app.ui.page_ajustements import render as render_adj
        render_adj(session)

# Footer
st.sidebar.divider()
st.sidebar.caption("v1.0 - Sage 100 GC")
