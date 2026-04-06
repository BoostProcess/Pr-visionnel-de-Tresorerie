"""Composants de filtrage réutilisables."""

from datetime import date

import streamlit as st

from config import SCENARIOS


MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

SCENARIO_LABELS = {
    "prudent": "Prudent",
    "central": "Central",
    "ambitieux": "Ambitieux",
}


def scenario_selector(key: str = "scenario") -> str:
    """Sélecteur de scénario."""
    options = SCENARIOS
    labels = [SCENARIO_LABELS[s] for s in options]
    idx = st.radio(
        "Scénario",
        range(len(options)),
        format_func=lambda i: labels[i],
        horizontal=True,
        key=key,
    )
    return options[idx]


def month_selector(key: str = "month", default: date | None = None) -> date:
    """Sélecteur de mois."""
    if default is None:
        default = date.today().replace(day=1)
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox(
            "Mois",
            range(1, 13),
            index=default.month - 1,
            format_func=lambda m: MOIS_FR[m - 1],
            key=f"{key}_month",
        )
    with col2:
        year = st.number_input(
            "Année",
            min_value=2020,
            max_value=2030,
            value=default.year,
            key=f"{key}_year",
        )
    return date(year, month, 1)


def format_xpf(montant: int) -> str:
    """Formate un montant en XPF avec séparateur de milliers."""
    if montant < 0:
        return f"-{abs(montant):,} F".replace(",", " ")
    return f"{montant:,} F".replace(",", " ")


def format_month_fr(d: date) -> str:
    """Formate une date en mois français."""
    return f"{MOIS_FR[d.month - 1]} {d.year}"
