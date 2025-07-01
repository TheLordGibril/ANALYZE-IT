# predict.py
from datetime import datetime
import random


def predict_pandemic(country: str, virus: str, date: str):
    """
    Calcule des prédictions pour un pays et un virus donnés à partir d'une date.
    Ici, c’est un mock pour l’exemple.
    """

    # TODO: charger et appeler tes vrais modèles ici
    # Fausses valeurs
    transmission_rate = [round(random.uniform(0.8, 1.5), 2) for _ in range(7)]
    mortality_rate = [round(random.uniform(0.01, 0.05), 4) for _ in range(7)]
    geographic_spread = ["France", "Italy", "Spain"]

    peak_date = "2025-08-15"
    estimated_duration_days = 120
    cases_in_30d = 200000
    deaths_in_30d = 5000
    new_countries_next_week = 2

    return {
        "country": country,
        "virus": virus,
        "predictions": {
            "transmission_rate": transmission_rate,
            "mortality_rate": mortality_rate,
            "geographic_spread": geographic_spread,
            "peak_date": peak_date,
            "estimated_duration_days": estimated_duration_days,
            "cases_in_30d": cases_in_30d,
            "deaths_in_30d": deaths_in_30d,
            "new_countries_next_week": new_countries_next_week
        }
    }
