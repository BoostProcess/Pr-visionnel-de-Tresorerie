"""Point d'entrée de l'application Streamlit."""

import streamlit as st

from app.models.database import init_db

# Initialiser la base de données
init_db()

st.set_page_config(
    page_title="Prévisionnel de Trésorerie",
    page_icon="💰",
    layout="wide",
)

st.title("Prévisionnel de Trésorerie")
st.info("Application en cours de construction.")
