"""Page 6 : Import de données Sage et contrôle des erreurs."""

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from app.imports.import_service import IMPORT_ORDER, ImportService
from app.models.imports_log import ErreurImport, LotImport


FILE_TYPE_LABELS = {
    "clients": "Clients",
    "fournisseurs": "Fournisseurs",
    "factures_clients": "Factures clients",
    "factures_fournisseurs": "Factures fournisseurs",
    "commandes_clients": "Commandes clients",
    "commandes_fournisseurs": "Commandes fournisseurs",
    "avoirs": "Avoirs",
    "historique": "Historique de facturation",
}


def render(session):
    """Affiche la page d'import."""
    st.header("Import des données Sage")

    tab1, tab2 = st.tabs(["Importer", "Journal des imports"])

    with tab1:
        _render_import_form(session)

    with tab2:
        _render_import_log(session)


def _render_import_form(session):
    """Formulaire d'import de fichiers."""
    st.subheader("Importer un fichier")

    st.info(
        "**Ordre d'import recommandé :** Clients → Fournisseurs → "
        "Factures → Commandes → Avoirs → Historique"
    )

    file_type = st.selectbox(
        "Type de fichier",
        IMPORT_ORDER,
        format_func=lambda t: FILE_TYPE_LABELS.get(t, t),
    )

    uploaded_file = st.file_uploader(
        "Fichier CSV ou Excel",
        type=["csv", "xlsx", "xls", "txt"],
        key="import_file",
    )

    encoding = st.selectbox(
        "Encodage",
        ["latin-1", "utf-8", "cp1252"],
        index=0,
    )

    if uploaded_file and st.button("Importer", type="primary"):
        with st.spinner(f"Import de {uploaded_file.name}..."):
            # Sauvegarder le fichier temporairement
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                service = ImportService(session)
                lot = service.import_file(tmp_path, file_type, encoding)
                session.commit()

                # Afficher le résultat
                if lot.statut == "succes":
                    st.success(
                        f"Import réussi : {lot.nb_importees} lignes importées "
                        f"sur {lot.nb_lignes}."
                    )
                elif lot.statut == "partiel":
                    st.warning(
                        f"Import partiel : {lot.nb_importees} importées, "
                        f"{lot.nb_doublons} doublons, {lot.nb_erreurs} erreurs."
                    )
                else:
                    st.error(f"Import échoué : {lot.nb_erreurs} erreurs.")

                # Afficher les erreurs
                if lot.nb_erreurs > 0 or lot.nb_doublons > 0:
                    _show_lot_errors(session, lot.id)

            except Exception as e:
                st.error(f"Erreur lors de l'import : {e}")
            finally:
                Path(tmp_path).unlink(missing_ok=True)


def _render_import_log(session):
    """Journal des imports passés."""
    st.subheader("Historique des imports")

    lots = (
        session.query(LotImport)
        .order_by(LotImport.date_import.desc())
        .limit(50)
        .all()
    )

    if not lots:
        st.info("Aucun import effectué.")
        return

    data = [{
        "Date": lot.date_import.strftime("%d/%m/%Y %H:%M"),
        "Fichier": lot.nom_fichier.split("/")[-1],
        "Type": FILE_TYPE_LABELS.get(lot.type_fichier, lot.type_fichier),
        "Lignes": lot.nb_lignes,
        "Importées": lot.nb_importees,
        "Doublons": lot.nb_doublons,
        "Erreurs": lot.nb_erreurs,
        "Statut": lot.statut,
    } for lot in lots]

    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    # Sélection d'un lot pour voir les détails
    lot_ids = [lot.id for lot in lots]
    lot_labels = [f"{lot.date_import.strftime('%d/%m %H:%M')} - {lot.nom_fichier.split('/')[-1]}" for lot in lots]

    selected = st.selectbox("Voir le détail d'un import", lot_labels, index=None)
    if selected:
        idx = lot_labels.index(selected)
        _show_lot_errors(session, lot_ids[idx])


def _show_lot_errors(session, lot_id: int):
    """Affiche les erreurs d'un lot d'import."""
    errors = (
        session.query(ErreurImport)
        .filter(ErreurImport.lot_id == lot_id)
        .order_by(ErreurImport.numero_ligne)
        .all()
    )

    if not errors:
        st.success("Aucune erreur pour ce lot.")
        return

    data = [{
        "Ligne": e.numero_ligne,
        "Type": e.type_erreur,
        "Champ": e.nom_champ or "-",
        "Valeur": e.valeur_brute or "-",
        "Message": e.message,
    } for e in errors]

    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
