"""Page 3 : Détail des décaissements."""

import streamlit as st

from app.services.forecast_service import ForecastService
from app.ui.components.data_tables import detail_lines_table
from app.ui.components.filters import month_selector, scenario_selector


def render(session):
    """Affiche le détail des décaissements."""
    st.header("Décaissements détaillés")

    service = ForecastService(session)

    if not service.has_forecast_data():
        st.warning("Aucun prévisionnel calculé.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        scenario = scenario_selector("dec_scenario")
    with col2:
        filter_month = st.checkbox("Filtrer par mois", key="dec_filter")
        selected_month = None
        if filter_month:
            selected_month = month_selector("dec_month")

    lines = service.get_decaissements(scenario, selected_month)

    categories = {}
    for line in lines:
        cat = line.categorie
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(line)

    cat_labels = {
        "decaissement_facture": "Factures fournisseurs",
        "decaissement_commande": "Commandes fournisseurs (prévisionnelles)",
        "charge_fixe": "Charges fixes",
        "emprunt": "Emprunts",
        "tva": "TVA",
        "charges_sociales": "Charges sociales",
        "impot": "Impôts et taxes",
        "avoir_client": "Avoirs clients",
        "ajustement_manuel": "Ajustements manuels",
    }

    for cat, cat_lines in categories.items():
        label = cat_labels.get(cat, cat)
        detail_lines_table(cat_lines, label)
