"""Page 1 : Dashboard de synthèse."""

import pandas as pd
import streamlit as st

from app.calculations.monthly_aggregator import MonthSummary
from app.ui.components.data_tables import forecast_summary_table
from app.ui.components.filters import (
    format_month_fr,
    format_xpf,
    scenario_selector,
)
from app.ui.components.kpi_cards import kpi_row


def render(forecast_data: dict[str, list[MonthSummary]]):
    """Affiche le dashboard de synthèse."""
    st.header("Synthèse du prévisionnel de trésorerie")

    if not forecast_data:
        st.warning("Aucun prévisionnel calculé. Lancez le calcul depuis l'onglet Hypothèses.")
        return

    scenario = scenario_selector("dashboard_scenario")
    summaries = forecast_data.get(scenario, [])

    if not summaries:
        st.info("Pas de données pour ce scénario.")
        return

    # KPIs
    first = summaries[0]
    last = summaries[-1]
    point_bas = min(summaries, key=lambda s: s.tresorerie_fin)
    total_enc = sum(s.total_encaissements for s in summaries)
    total_dec = sum(s.total_decaissements for s in summaries)

    kpi_row([
        ("Trésorerie actuelle", first.tresorerie_debut, None),
        ("Trésorerie fin période", last.tresorerie_fin, None),
        ("Point bas", point_bas.tresorerie_fin, format_month_fr(point_bas.mois)),
        ("Total encaissements", total_enc, None),
        ("Total décaissements", abs(total_dec), None),
    ])

    st.divider()

    # Graphique
    _render_chart(summaries)

    st.divider()

    # Comparaison 3 scénarios
    _render_scenario_comparison(forecast_data)

    st.divider()

    # Tableau de synthèse
    forecast_summary_table(summaries, f"Détail mensuel - Scénario {scenario.capitalize()}")

    # Export Excel
    st.divider()
    _render_export(forecast_data)


def _render_chart(summaries: list[MonthSummary]):
    """Graphique barres + courbe."""
    data = []
    for s in summaries:
        data.append({
            "Mois": format_month_fr(s.mois),
            "Encaissements": s.total_encaissements,
            "Décaissements": abs(s.total_decaissements),
            "Trésorerie fin": s.tresorerie_fin,
        })

    df = pd.DataFrame(data)
    st.subheader("Évolution mensuelle")

    # Barres encaissements / décaissements
    chart_data = df[["Mois", "Encaissements", "Décaissements"]].set_index("Mois")
    st.bar_chart(chart_data)

    # Courbe trésorerie
    st.subheader("Trésorerie fin de mois")
    treso_data = df[["Mois", "Trésorerie fin"]].set_index("Mois")
    st.line_chart(treso_data)


def _render_scenario_comparison(forecast_data: dict[str, list[MonthSummary]]):
    """Tableau comparatif des 3 scénarios."""
    st.subheader("Comparaison des scénarios")

    rows = []
    for scenario, summaries in forecast_data.items():
        if not summaries:
            continue
        total_enc = sum(s.total_encaissements for s in summaries)
        total_dec = sum(s.total_decaissements for s in summaries)
        point_bas = min(s.tresorerie_fin for s in summaries)
        treso_fin = summaries[-1].tresorerie_fin

        rows.append({
            "Scénario": scenario.capitalize(),
            "Encaissements": format_xpf(total_enc),
            "Décaissements": format_xpf(abs(total_dec)),
            "Point bas": format_xpf(point_bas),
            "Trésorerie fin": format_xpf(treso_fin),
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_export(forecast_data: dict[str, list[MonthSummary]]):
    """Bouton d'export Excel."""
    from app.exports.excel_export import ExcelExporter

    st.subheader("Export Excel")
    if st.button("Générer le fichier Excel", type="primary"):
        exporter = ExcelExporter()
        excel_buffer = exporter.export(forecast_data)
        st.download_button(
            label="Télécharger le prévisionnel (.xlsx)",
            data=excel_buffer,
            file_name="previsionnel_tresorerie.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
