"""Page 7 : Journal des ajustements manuels."""

from datetime import date

import pandas as pd
import streamlit as st

from app.services.referentiel_service import ReferentielService
from app.ui.components.filters import MOIS_FR, format_xpf


def render(session):
    """Affiche la page des ajustements manuels."""
    st.header("Ajustements manuels")

    service = ReferentielService(session)

    # Formulaire d'ajout
    with st.expander("Ajouter un ajustement", expanded=True):
        with st.form("add_adjustment"):
            col1, col2 = st.columns(2)
            with col1:
                mois_num = st.selectbox(
                    "Mois",
                    range(1, 13),
                    format_func=lambda m: MOIS_FR[m - 1],
                )
                annee = st.number_input("Année", value=date.today().year, min_value=2020, max_value=2030)
            with col2:
                direction = st.selectbox(
                    "Type",
                    ["encaissement", "decaissement"],
                    format_func=lambda d: "Encaissement" if d == "encaissement" else "Décaissement",
                )
                montant = st.number_input("Montant (F)", value=0, step=10000, min_value=0)

            libelle = st.text_input("Libellé")
            categorie = st.selectbox(
                "Catégorie",
                ["client_exceptionnel", "fournisseur_exceptionnel", "subvention",
                 "investissement", "cession", "autre"],
            )
            notes = st.text_area("Notes", height=80)

            if st.form_submit_button("Ajouter l'ajustement"):
                if libelle and montant > 0:
                    mois_date = date(annee, mois_num, 1)
                    service.create_ajustement(
                        mois=mois_date,
                        direction=direction,
                        libelle=libelle,
                        montant=montant,
                        categorie=categorie,
                        notes=notes or None,
                    )
                    session.commit()
                    st.success(f"Ajustement '{libelle}' ajouté pour {MOIS_FR[mois_num - 1]} {annee}.")
                    st.rerun()
                else:
                    st.error("Veuillez remplir le libellé et un montant > 0.")

    # Liste des ajustements existants
    st.subheader("Ajustements enregistrés")
    ajustements = service.list_ajustements()

    if not ajustements:
        st.info("Aucun ajustement manuel.")
        return

    data = []
    for adj in ajustements:
        data.append({
            "id": adj.id,
            "Mois": f"{MOIS_FR[adj.mois.month - 1]} {adj.mois.year}",
            "Type": "Encaissement" if adj.direction == "encaissement" else "Décaissement",
            "Libellé": adj.libelle,
            "Montant": format_xpf(adj.montant),
            "Catégorie": adj.categorie,
            "Notes": adj.notes or "",
        })

    df = pd.DataFrame(data)
    st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

    # Suppression
    adj_to_delete = st.selectbox(
        "Supprimer un ajustement",
        [(a["id"], f"{a['Mois']} - {a['Libellé']} ({a['Montant']})") for a in data],
        format_func=lambda x: x[1],
        index=None,
    )
    if adj_to_delete and st.button("Supprimer", type="secondary"):
        service.delete_ajustement(adj_to_delete[0])
        session.commit()
        st.success("Ajustement supprimé.")
        st.rerun()
