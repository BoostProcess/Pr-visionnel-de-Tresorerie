"""Page Analyse Financière - États de synthèse depuis le FEC.

Inspiré de Finthesis : reconstitution automatique du compte de résultat,
SIG, KPIs, et graphiques depuis les écritures comptables.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.services.fec_analysis_service import FECAnalysisService
from app.ui.components.filters import format_xpf
from app.ui.components.kpi_cards import kpi_row


def render(session):
    """Affiche la page d'analyse financière FEC."""
    st.header("Analyse financière")

    service = FECAnalysisService(session)

    if not service.has_fec_data():
        st.warning(
            "Aucune écriture FEC en base. Importez un fichier FEC depuis "
            "l'onglet **Imports** pour activer les analyses financières."
        )
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "KPIs",
        "Compte de résultat",
        "Flux de trésorerie",
        "Budget vs Réel",
    ])

    with tab1:
        _render_kpis(service)
    with tab2:
        _render_compte_resultat(service)
    with tab3:
        _render_flux_tresorerie(service)
    with tab4:
        _render_budget_vs_reel(service)


def _render_kpis(service: FECAnalysisService):
    """Affiche les KPIs financiers clés."""
    st.subheader("Indicateurs clés de performance")

    kpis = service.compute_kpis()

    # Ligne 1 : Activité
    kpi_row([
        ("Chiffre d'affaires", kpis.chiffre_affaires, None),
        ("Marge brute", kpis.marge_brute, f"{kpis.taux_marge_brute}%"),
        ("Valeur ajoutée", kpis.valeur_ajoutee, None),
        ("EBE", kpis.ebe, f"{kpis.taux_ebe}%"),
    ])

    st.divider()

    # Ligne 2 : Résultat et trésorerie
    kpi_row([
        ("Résultat net", kpis.resultat_net, None),
        ("CAF", kpis.caf, None),
        ("BFR", kpis.bfr, None),
        ("Trésorerie nette", kpis.tresorerie_nette, None),
    ])

    st.divider()

    # Ligne 3 : Délais de paiement
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Créances clients", format_xpf(kpis.creances_clients))
    with col2:
        st.metric("DSO (délai clients)", f"{kpis.dso_jours} jours")
    with col3:
        st.metric("Dettes fournisseurs", format_xpf(kpis.dettes_fournisseurs))
    with col4:
        st.metric("DPO (délai fournisseurs)", f"{kpis.dpo_jours} jours")


def _render_compte_resultat(service: FECAnalysisService):
    """Affiche le compte de résultat et les SIG."""
    st.subheader("Compte de résultat")

    cr = service.compute_compte_resultat()

    # SIG (Soldes Intermédiaires de Gestion)
    sig_data = [
        {"Indicateur": "Chiffre d'affaires", "Montant": cr.chiffre_affaires, "type": "produit"},
        {"Indicateur": "- Achats consommés", "Montant": -cr.achats, "type": "charge"},
        {"Indicateur": "= Marge brute", "Montant": cr.marge_brute, "type": "solde"},
        {"Indicateur": "- Charges externes", "Montant": -cr.charges_externes, "type": "charge"},
        {"Indicateur": "+ Autres produits", "Montant": cr.autres_produits, "type": "produit"},
        {"Indicateur": "= Valeur ajoutée", "Montant": cr.valeur_ajoutee, "type": "solde"},
        {"Indicateur": "- Impôts et taxes", "Montant": -cr.impots_taxes, "type": "charge"},
        {"Indicateur": "- Charges de personnel", "Montant": -cr.charges_personnel, "type": "charge"},
        {"Indicateur": "= EBE (Excédent Brut d'Exploitation)", "Montant": cr.ebe, "type": "solde"},
        {"Indicateur": "- Dotations amortissements", "Montant": -cr.dotations_amortissements, "type": "charge"},
        {"Indicateur": "= Résultat d'exploitation", "Montant": cr.resultat_exploitation, "type": "solde"},
        {"Indicateur": "+ Produits financiers", "Montant": cr.produits_financiers, "type": "produit"},
        {"Indicateur": "- Charges financières", "Montant": -cr.charges_financieres, "type": "charge"},
        {"Indicateur": "= Résultat courant", "Montant": cr.resultat_courant, "type": "solde"},
        {"Indicateur": "+ Produits exceptionnels", "Montant": cr.produits_exceptionnels, "type": "produit"},
        {"Indicateur": "- Charges exceptionnelles", "Montant": -cr.charges_exceptionnelles, "type": "charge"},
        {"Indicateur": "- Impôt sur les bénéfices", "Montant": -cr.impot_benefice, "type": "charge"},
        {"Indicateur": "= Résultat net", "Montant": cr.resultat_net, "type": "solde"},
        {"Indicateur": "CAF (Capacité d'Autofinancement)", "Montant": cr.caf, "type": "solde"},
    ]

    df = pd.DataFrame(sig_data)
    df["Montant (XPF)"] = df["Montant"].apply(format_xpf)

    # Affichage avec mise en forme
    st.dataframe(
        df[["Indicateur", "Montant (XPF)"]],
        use_container_width=True,
        hide_index=True,
    )

    # Graphique waterfall du SIG
    st.subheader("Cascade des SIG (Waterfall)")
    _render_waterfall_sig(cr)


def _render_waterfall_sig(cr):
    """Graphique waterfall des Soldes Intermédiaires de Gestion."""
    fig = go.Figure(go.Waterfall(
        name="SIG",
        orientation="v",
        measure=[
            "absolute", "relative", "relative", "relative",
            "total",
            "relative", "relative",
            "total",
        ],
        x=[
            "CA", "Achats", "Charges ext.", "Personnel",
            "EBE",
            "Amort.", "Financier",
            "Résultat net",
        ],
        y=[
            cr.chiffre_affaires,
            -cr.achats,
            -cr.charges_externes - cr.impots_taxes,
            -cr.charges_personnel,
            0,  # total
            -cr.dotations_amortissements,
            cr.resultat_financier,
            0,  # total
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2ecc71"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#3498db"}},
    ))

    fig.update_layout(
        title="Du Chiffre d'Affaires au Résultat Net",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_flux_tresorerie(service: FECAnalysisService):
    """Affiche le tableau de flux de trésorerie."""
    st.subheader("Tableau de flux de trésorerie")

    ft = service.compute_flux_tresorerie()

    flux_data = [
        {"Catégorie": "FLUX D'EXPLOITATION", "Montant": "", "type": "header"},
        {"Catégorie": "Résultat net", "Montant": ft.resultat_net, "type": "detail"},
        {"Catégorie": "+ Dotations amortissements", "Montant": ft.dotations_amortissements, "type": "detail"},
        {"Catégorie": "- Variation des stocks", "Montant": -ft.variation_stocks, "type": "detail"},
        {"Catégorie": "- Variation des créances", "Montant": -ft.variation_creances, "type": "detail"},
        {"Catégorie": "+ Variation des dettes", "Montant": ft.variation_dettes, "type": "detail"},
        {"Catégorie": "= Flux d'exploitation", "Montant": ft.flux_exploitation, "type": "total"},
        {"Catégorie": "", "Montant": "", "type": "spacer"},
        {"Catégorie": "FLUX D'INVESTISSEMENT", "Montant": "", "type": "header"},
        {"Catégorie": "- Acquisitions immobilisations", "Montant": -ft.acquisitions_immo, "type": "detail"},
        {"Catégorie": "+ Cessions immobilisations", "Montant": ft.cessions_immo, "type": "detail"},
        {"Catégorie": "= Flux d'investissement", "Montant": ft.flux_investissement, "type": "total"},
        {"Catégorie": "", "Montant": "", "type": "spacer"},
        {"Catégorie": "FLUX DE FINANCEMENT", "Montant": "", "type": "header"},
        {"Catégorie": "+ Nouveaux emprunts", "Montant": ft.emprunts_nouveaux, "type": "detail"},
        {"Catégorie": "- Remboursements emprunts", "Montant": -ft.remboursements_emprunts, "type": "detail"},
        {"Catégorie": "+ Apports en capital", "Montant": ft.apports_capital, "type": "detail"},
        {"Catégorie": "- Dividendes versés", "Montant": -ft.dividendes, "type": "detail"},
        {"Catégorie": "= Flux de financement", "Montant": ft.flux_financement, "type": "total"},
        {"Catégorie": "", "Montant": "", "type": "spacer"},
        {"Catégorie": "VARIATION DE TRÉSORERIE", "Montant": ft.variation_tresorerie, "type": "grandtotal"},
    ]

    rows = []
    for item in flux_data:
        if item["type"] == "spacer":
            continue
        montant = item["Montant"]
        rows.append({
            "Catégorie": item["Catégorie"],
            "Montant (XPF)": format_xpf(montant) if isinstance(montant, int) else "",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Graphique waterfall des flux
    st.subheader("Décomposition des flux")
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Exploitation", "Investissement", "Financement", "Variation trésorerie"],
        y=[ft.flux_exploitation, ft.flux_investissement, ft.flux_financement, 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2ecc71"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#3498db"}},
    ))
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _render_budget_vs_reel(service: FECAnalysisService):
    """Comparaison Budget vs Réel + évolution mensuelle du CA."""
    st.subheader("Évolution mensuelle du chiffre d'affaires")

    ca_mensuel = service.compute_ca_mensuel()

    if not ca_mensuel:
        st.info("Pas de données de CA mensuel disponibles.")
        return

    # Graphique d'évolution
    mois_tries = sorted(ca_mensuel.keys())
    montants = [ca_mensuel[m] for m in mois_tries]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mois_tries,
        y=montants,
        name="CA Réel",
        marker_color="#3498db",
    ))
    fig.update_layout(
        title="Chiffre d'affaires mensuel",
        xaxis_title="Mois",
        yaxis_title="Montant (XPF)",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau détaillé
    df = pd.DataFrame({
        "Mois": mois_tries,
        "CA (XPF)": [format_xpf(m) for m in montants],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info(
        "Pour comparer Budget vs Réel, saisissez vos hypothèses budgétaires "
        "dans l'onglet **Hypothèses** puis relancez le calcul."
    )
