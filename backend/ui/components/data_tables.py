"""Composants de tableaux de données."""

import pandas as pd
import streamlit as st

from app.ui.components.filters import format_xpf, format_month_fr


def forecast_summary_table(summaries: list, title: str = "Synthèse mensuelle"):
    """Affiche le tableau de synthèse mensuelle."""
    if not summaries:
        st.info("Aucune donnée de prévisionnel.")
        return

    data = []
    for s in summaries:
        data.append({
            "Mois": format_month_fr(s.mois),
            "Trésorerie début": s.tresorerie_debut,
            "Encaissements": s.total_encaissements,
            "Décaissements": s.total_decaissements,
            "Flux net": s.flux_net,
            "Trésorerie fin": s.tresorerie_fin,
        })

    df = pd.DataFrame(data)

    # Formater les colonnes monétaires
    money_cols = ["Trésorerie début", "Encaissements", "Décaissements", "Flux net", "Trésorerie fin"]
    for col in money_cols:
        df[col] = df[col].apply(format_xpf)

    st.subheader(title)
    st.dataframe(df, use_container_width=True, hide_index=True)


def detail_lines_table(lines: list, title: str = "Détail"):
    """Affiche un tableau détaillé de lignes de prévisionnel."""
    if not lines:
        st.info("Aucune ligne.")
        return

    data = []
    for line in lines:
        data.append({
            "Mois": format_month_fr(line.mois),
            "Date échéance": line.date_echeance.strftime("%d/%m/%Y") if line.date_echeance else "",
            "Tiers": line.nom_tiers or "",
            "Catégorie": line.categorie,
            "Sous-catégorie": line.sous_categorie or "",
            "Montant": line.montant,
            "Source": line.source_type or "",
        })

    df = pd.DataFrame(data)
    df["Montant"] = df["Montant"].apply(format_xpf)

    st.subheader(title)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Sous-total
    total = sum(line.montant for line in lines)
    st.markdown(f"**Total : {format_xpf(total)}**")
