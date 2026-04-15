"""Configuration globale de l'application."""

import os

# Base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tresorerie.db")

# Devise
CURRENCY = "XPF"
CURRENCY_SYMBOL = "F"

# Prévisionnel
FORECAST_MONTHS = 24
SCENARIOS = ["prudent", "central", "ambitieux"]

# Ajustements par scénario (jours de décalage)
SCENARIO_ADJUSTMENTS = {
    "prudent": {
        "retard_client_jours": 15,
        "taux_conversion_commandes": -0.20,  # -20%
        "avance_fournisseur_jours": 0,
    },
    "central": {
        "retard_client_jours": 0,
        "taux_conversion_commandes": 0.0,
        "avance_fournisseur_jours": 0,
    },
    "ambitieux": {
        "retard_client_jours": -5,
        "taux_conversion_commandes": 0.10,  # +10%
        "avance_fournisseur_jours": 5,
    },
}

# TVA Polynésie Française
TVA_RATES = {
    "normal": 0.16,
    "intermediaire": 0.13,
    "reduit": 0.05,
    "exonere": 0.0,
}
TVA_DEFAULT_RATE = "normal"

# Import Sage
SAGE_ENCODING = "latin-1"
SAGE_CSV_SEPARATOR = ";"
SAGE_DATE_FORMATS = ["%d/%m/%Y", "%Y%m%d", "%Y-%m-%d"]
SAGE_DECIMAL_SEPARATOR = ","
