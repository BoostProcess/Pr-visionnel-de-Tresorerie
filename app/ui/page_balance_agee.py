"""Page Balance Âgée - Détail auxiliaire clients et fournisseurs.

Inspiré de Finthesis : analyse des créances et dettes par ancienneté.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.services.fec_analysis_service import FECAnalysisService, LigneBalanceAgee
from app.ui.components.filters import format_xpf


def render(session):
    """Affiche la page de balance âgée."""
    st.header("Balance âgée")

    service = FECAnalysisService(session)

    tab1, tab2 = st.tabs(["Clients", "Fournisseurs"])

    with tab1:
        _render_balance_clients(service)
    with tab2:
        _render_balance_fournisseurs(service)


def _render_balance_clients(service: FECAnalysisService):
    """Balance âgée des créances clients."""
    st.subheader("Créances clients par ancienneté")

    lignes = service.compute_balance_agee_clients()

    if not lignes:
        st.info("Aucune créance client ouverte.")
        return

    _render_balance_table(lignes, "client")
    _render_balance_chart(lignes, "Créances clients")


def _render_balance_fournisseurs(service: FECAnalysisService):
    """Balance âgée des dettes fournisseurs."""
    st.subheader("Dettes fournisseurs par ancienneté")

    lignes = service.compute_balance_agee_fournisseurs()

    if not lignes:
        st.info("Aucune dette fournisseur ouverte.")
        return

    _render_balance_table(lignes, "fournisseur")
    _render_balance_chart(lignes, "Dettes fournisseurs")


def _render_balance_table(lignes: list[LigneBalanceAgee], type_tiers: str):
    """Tableau de la balance âgée."""
    data = []
    for l in lignes:
        data.append({
            "Code": l.code,
            "Nom": l.nom,
            "Total": l.total,
            "Non échu": l.non_echu,
            "0-30 j": l.echu_0_30,
            "30-60 j": l.echu_30_60,
            "60-90 j": l.echu_60_90,
            "+90 j": l.echu_plus_90,
        })

    df = pd.DataFrame(data)

    # Ligne de totaux
    total_row = {
        "Code": "",
        "Nom": "TOTAL",
        "Total": df["Total"].sum(),
        "Non échu": df["Non échu"].sum(),
        "0-30 j": df["0-30 j"].sum(),
        "30-60 j": df["30-60 j"].sum(),
        "60-90 j": df["60-90 j"].sum(),
        "+90 j": df["+90 j"].sum(),
    }
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    # Formater les montants
    for col in ["Total", "Non échu", "0-30 j", "30-60 j", "60-90 j", "+90 j"]:
        df[col] = df[col].apply(lambda x: format_xpf(x) if x != 0 else "-")

    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_balance_chart(lignes: list[LigneBalanceAgee], title: str):
    """Graphique de répartition par ancienneté."""
    total_non_echu = sum(l.non_echu for l in lignes)
    total_0_30 = sum(l.echu_0_30 for l in lignes)
    total_30_60 = sum(l.echu_30_60 for l in lignes)
    total_60_90 = sum(l.echu_60_90 for l in lignes)
    total_90p = sum(l.echu_plus_90 for l in lignes)

    values = [total_non_echu, total_0_30, total_30_60, total_60_90, total_90p]
    labels = ["Non échu", "0-30 jours", "30-60 jours", "60-90 jours", "+90 jours"]
    colors = ["#2ecc71", "#f39c12", "#e67e22", "#e74c3c", "#c0392b"]

    # Ne garder que les valeurs non nulles
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]

    if not filtered:
        return

    fig = go.Figure(data=[go.Pie(
        labels=[f[0] for f in filtered],
        values=[f[1] for f in filtered],
        marker_colors=[f[2] for f in filtered],
        hole=0.4,
        textinfo="label+percent",
    )])
    fig.update_layout(
        title=f"Répartition par ancienneté - {title}",
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)
