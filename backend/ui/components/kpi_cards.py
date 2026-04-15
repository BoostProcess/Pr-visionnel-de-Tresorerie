"""Cartes d'indicateurs clés (KPI)."""

import streamlit as st

from app.ui.components.filters import format_xpf


def kpi_row(metrics: list[tuple[str, int, str | None]]):
    """Affiche une ligne de KPIs.

    Args:
        metrics: liste de (label, valeur, delta_label optionnel)
    """
    cols = st.columns(len(metrics))
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            st.metric(
                label=label,
                value=format_xpf(value),
                delta=delta,
            )
