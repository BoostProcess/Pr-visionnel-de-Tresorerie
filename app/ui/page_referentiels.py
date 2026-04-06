"""Page 5 : Gestion des référentiels."""

from datetime import date

import pandas as pd
import streamlit as st

from app.services.referentiel_service import ReferentielService
from app.ui.components.filters import format_xpf


def render(session):
    """Affiche et permet de gérer les référentiels."""
    st.header("Référentiels")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Conditions de règlement",
        "Clients",
        "Fournisseurs",
        "Charges fixes",
        "Emprunts",
    ])

    service = ReferentielService(session)

    with tab1:
        _render_conditions(service, session)
    with tab2:
        _render_clients(service)
    with tab3:
        _render_fournisseurs(service)
    with tab4:
        _render_charges_fixes(service, session)
    with tab5:
        _render_emprunts(service, session)


def _render_conditions(service: ReferentielService, session):
    """Gestion des conditions de règlement."""
    st.subheader("Conditions de règlement")

    conditions = service.list_conditions()
    if conditions:
        data = [{
            "Code": c.code,
            "Libellé": c.libelle,
            "Jours": c.base_jours,
            "Fin de mois": "Oui" if c.fin_de_mois else "Non",
            "Jour fixe": c.jour_du_mois or "-",
        } for c in conditions]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Aucune condition de règlement.")

    with st.expander("Ajouter une condition"):
        with st.form("add_condition"):
            code = st.text_input("Code (ex: 30FM, 60NET)")
            libelle = st.text_input("Libellé (ex: 30 jours fin de mois)")
            base_jours = st.number_input("Nombre de jours", value=30, min_value=0, max_value=365)
            fin_de_mois = st.checkbox("Fin de mois")
            jour_du_mois = st.number_input(
                "Jour du mois (0 = pas de jour fixe)", value=0, min_value=0, max_value=31,
            )

            if st.form_submit_button("Ajouter"):
                if code and libelle:
                    service.create_condition(
                        code=code,
                        libelle=libelle,
                        base_jours=base_jours,
                        fin_de_mois=fin_de_mois,
                        jour_du_mois=jour_du_mois if jour_du_mois > 0 else None,
                    )
                    session.commit()
                    st.success(f"Condition '{code}' ajoutée.")
                    st.rerun()


def _render_clients(service: ReferentielService):
    """Liste des clients."""
    st.subheader("Clients")
    clients = service.list_clients()
    if clients:
        data = [{
            "Code Sage": c.sage_code,
            "Nom": c.name,
            "Condition": c.condition_reglement.code if c.condition_reglement else "-",
            "Activité": c.code_activite or "-",
            "Actif": "Oui" if c.is_active else "Non",
        } for c in clients]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Aucun client. Importez les données depuis l'onglet Imports.")


def _render_fournisseurs(service: ReferentielService):
    """Liste des fournisseurs."""
    st.subheader("Fournisseurs")
    fournisseurs = service.list_fournisseurs()
    if fournisseurs:
        data = [{
            "Code Sage": f.sage_code,
            "Nom": f.name,
            "Condition": f.condition_reglement.code if f.condition_reglement else "-",
            "Activité": f.code_activite or "-",
            "Actif": "Oui" if f.is_active else "Non",
        } for f in fournisseurs]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Aucun fournisseur. Importez les données depuis l'onglet Imports.")


def _render_charges_fixes(service: ReferentielService, session):
    """Gestion des charges fixes."""
    st.subheader("Charges fixes")

    charges = service.list_charges_fixes()
    if charges:
        data = [{
            "Libellé": c.libelle,
            "Catégorie": c.categorie,
            "Montant TTC": format_xpf(c.montant_ttc),
            "Fréquence": c.frequence,
            "Jour paiement": c.jour_paiement,
            "Actif": "Oui" if c.is_active else "Non",
        } for c in charges]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with st.expander("Ajouter une charge fixe"):
        with st.form("add_charge"):
            libelle = st.text_input("Libellé")
            categorie = st.selectbox(
                "Catégorie",
                ["loyer", "assurance", "telecom", "electricite", "eau",
                 "entretien", "comptable", "logiciel", "autre"],
            )
            montant = st.number_input("Montant TTC (F)", value=0, step=10000)
            frequence = st.selectbox("Fréquence", ["mensuel", "trimestriel", "annuel"])
            jour = st.number_input("Jour de paiement", value=5, min_value=1, max_value=28)
            date_debut = st.date_input("Date de début")

            if st.form_submit_button("Ajouter"):
                if libelle and montant > 0:
                    service.create_charge_fixe(
                        libelle=libelle,
                        categorie=categorie,
                        montant_ttc=montant,
                        frequence=frequence,
                        jour_paiement=jour,
                        date_debut=date_debut,
                    )
                    session.commit()
                    st.success(f"Charge '{libelle}' ajoutée.")
                    st.rerun()


def _render_emprunts(service: ReferentielService, session):
    """Gestion des emprunts."""
    st.subheader("Emprunts")

    emprunts = service.list_emprunts()
    if emprunts:
        data = [{
            "Libellé": e.libelle,
            "Prêteur": e.preteur,
            "Mensualité": format_xpf(e.mensualite),
            "Capital restant": format_xpf(e.capital_restant),
            "Fin": e.date_fin.strftime("%m/%Y"),
            "Actif": "Oui" if e.is_active else "Non",
        } for e in emprunts]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with st.expander("Ajouter un emprunt"):
        with st.form("add_emprunt"):
            libelle = st.text_input("Libellé")
            preteur = st.text_input("Prêteur")
            montant_initial = st.number_input("Montant initial (F)", value=0, step=100000)
            capital_restant = st.number_input("Capital restant (F)", value=0, step=100000)
            mensualite = st.number_input("Mensualité (F)", value=0, step=10000)
            jour = st.number_input("Jour de prélèvement", value=5, min_value=1, max_value=28)
            date_debut = st.date_input("Date début", key="emprunt_debut")
            date_fin = st.date_input("Date fin", key="emprunt_fin")

            if st.form_submit_button("Ajouter"):
                if libelle and mensualite > 0:
                    service.create_emprunt(
                        libelle=libelle,
                        preteur=preteur,
                        montant_initial=montant_initial,
                        capital_restant=capital_restant,
                        mensualite=mensualite,
                        part_interet=0,
                        part_capital=0,
                        jour_paiement=jour,
                        date_debut=date_debut,
                        date_fin=date_fin,
                    )
                    session.commit()
                    st.success(f"Emprunt '{libelle}' ajouté.")
                    st.rerun()
