import joblib
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, Table, MetaData, and_
from config import config
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des modèles une seule fois au démarrage
logger.info("Chargement des modèles...")
try:
    new_cases_model = joblib.load("models/new_cases_model.joblib")
    new_deaths_model = joblib.load("models/new_deaths_model.joblib")
    infection_rate_model = joblib.load("models/infection_rate_model.joblib")
    mortality_rate_model = joblib.load("models/mortality_rate_model.joblib")
    total_cases_model = joblib.load("models/total_cases_model.joblib")
    total_deaths_model = joblib.load("models/total_deaths_model.joblib")
    peak_date_model = joblib.load("models/peak_date_model.joblib")
    estimated_duration_model = joblib.load("models/estimated_duration_model.joblib")
    cases_in_30d_model = joblib.load("models/cases_in_30d_model.joblib")
    deaths_in_30d_model = joblib.load("models/deaths_in_30d_model.joblib")
    geographic_spread_model = joblib.load("models/geographic_spread_model.joblib")
    new_countries_next_week_model = joblib.load("models/new_countries_next_week_model.joblib")
    logger.info("Modèles chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des modèles: {e}")
    raise


def get_country_id(country_name):
    engine = create_engine(config.get_database_url())
    meta = MetaData()
    pays = Table('Pays', meta, autoload_with=engine)
    with engine.connect() as conn:
        result = conn.execute(select(pays.c.id_pays).where(
            pays.c.nom_pays == country_name)).first()
        if result:
            return result[0]
        raise ValueError(f"Pays inconnu: {country_name}")


def get_virus_id(virus_name):
    engine = create_engine(config.get_database_url())
    meta = MetaData()
    virus = Table('Virus', meta, autoload_with=engine)
    with engine.connect() as conn:
        result = conn.execute(select(virus.c.id_virus).where(
            virus.c.nom_virus == virus_name)).first()
        if result:
            return result[0]
        raise ValueError(f"Virus inconnu: {virus_name}")


def get_official_data(country_id, virus_id, date_start, date_end):
    try:
        engine = create_engine(config.get_database_url())
        meta = MetaData()
        stats = Table('Statistiques_Journalieres', meta, autoload_with=engine)

        with engine.connect() as conn:
            query = select(
                stats.c.date,
                stats.c.nouveaux_cas,
                stats.c.nouveaux_deces,
                stats.c.total_cas,
                stats.c.total_deces,
                stats.c.taux_infection,
                stats.c.taux_mortalite,
                stats.c.croissance_cas,
                stats.c.taux_mortalite_population,
                stats.c.taux_infection_vs_global,
                stats.c.taux_mortalite_pop_vs_global
            ).where(
                and_(
                    stats.c.id_pays == country_id,
                    stats.c.id_virus == virus_id,
                    stats.c.date >= date_start,
                    stats.c.date <= date_end
                )
            ).order_by(stats.c.date)

            results = conn.execute(query).fetchall()
            logger.info(f"Données officielles récupérées: {len(results)} enregistrements")

            # Construire le dictionnaire des données officielles
            official_data = {}
            for row in results:
                date_str = row.date.strftime("%Y-%m-%d")
                official_data[date_str] = {
                    "nouveaux_cas": int(row.nouveaux_cas) if row.nouveaux_cas is not None else 0,
                    "nouveaux_deces": int(row.nouveaux_deces) if row.nouveaux_deces is not None else 0,
                    "total_cas": int(row.total_cas) if row.total_cas is not None else 0,
                    "total_deces": int(row.total_deces) if row.total_deces is not None else 0,
                    "taux_infection": float(row.taux_infection) if row.taux_infection is not None else 0.0,
                    "taux_mortalite": float(row.taux_mortalite) if row.taux_mortalite is not None else 0.0,
                    "croissance_cas": float(row.croissance_cas) if row.croissance_cas is not None else 0.0,
                    "taux_mortalite_population": float(
                        row.taux_mortalite_population) if row.taux_mortalite_population is not None else 0.0,
                    "taux_infection_vs_global": float(
                        row.taux_infection_vs_global) if row.taux_infection_vs_global is not None else 0.0,
                    "taux_mortalite_pop_vs_global": float(
                        row.taux_mortalite_pop_vs_global) if row.taux_mortalite_pop_vs_global is not None else 0.0
                }

            return official_data
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données officielles: {e}")
        raise


def get_dates_to_predict(all_dates, official_data):
    today = datetime.now().date()

    # Filtrer pour ne garder que les dates futures qui n'ont pas de données officielles
    dates_to_predict = []
    for date in all_dates:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        if date_obj >= today and date not in official_data:
            dates_to_predict.append(date)

    return dates_to_predict


def predict_single_day(country_id, virus_id, date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday

    # Features pour les prédictions
    X = np.array([[country_id, virus_id, year, day_of_year]])
    X_geo = np.array([[virus_id, year]])

    return {
        "nouveaux_cas": max(0, int(new_cases_model.predict(X)[0])),
        "nouveaux_deces": max(0, int(new_deaths_model.predict(X)[0])),
        "total_cas": max(0, int(total_cases_model.predict(X)[0])),
        "total_deces": max(0, int(total_deaths_model.predict(X)[0])),
        "taux_infection": max(0.0, float(infection_rate_model.predict(X)[0])),
        "taux_mortalite": max(0.0, float(mortality_rate_model.predict(X)[0])),
        "geographic_spread": max(0, int(geographic_spread_model.predict(X_geo)[0]))
    }



def generate_predictions(country_id, virus_id, dates_to_predict):
    if not dates_to_predict:
        return {}

    logger.info(f"Génération des prédictions pour {len(dates_to_predict)} dates")
    prediction_data = {}

    for date_str in dates_to_predict:
        prediction_data[date_str] = predict_single_day(country_id, virus_id, date_str)

    return prediction_data


def predict_pandemic(country: str, virus: str, date_start: str, date_end: str):
    """
    Calcule des prédictions pour un pays et un virus donnés sur une période.=
    """
    try:
        # Validation des dates
        d_start = datetime.strptime(date_start, "%Y-%m-%d")
        d_end = datetime.strptime(date_end, "%Y-%m-%d")

        if d_start > d_end:
            raise ValueError("La date de début doit être antérieure à la date de fin")

        nb_days = (d_end - d_start).days + 1

        # Récupération des IDs
        country_id = get_country_id(country)
        virus_id = get_virus_id(virus)

        # Génération de toutes les dates de la période
        all_dates = [(d_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(nb_days)]

        # Récupération des données officielles
        official_raw_data = get_official_data(country_id, virus_id, date_start, date_end)

        # Identification des dates à prédire
        dates_to_predict = get_dates_to_predict(all_dates, official_raw_data)

        # Génération des prédictions uniquement pour les dates nécessaires
        prediction_raw_data = generate_predictions(country_id, virus_id, dates_to_predict)

        total_cases = max(0, int(total_cases_model.predict(np.array([[country_id, virus_id, d_end.year, d_end.timetuple().tm_yday]]))[0]))
        total_deaths = max(0, int(total_deaths_model.predict(np.array([[country_id, virus_id, d_end.year, d_end.timetuple().tm_yday]]))[0]))

        peak_day_of_year = int(peak_date_model.predict(np.array([[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0])
        peak_date = datetime(d_start.year, 1, 1) + timedelta(days=peak_day_of_year - 1)
        peak_date_str = peak_date.strftime("%Y-%m-%d")

        estimated_duration_days = max(1, int(estimated_duration_model.predict(np.array([[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0]))
        cases_in_30d = max(0, int(cases_in_30d_model.predict(np.array([[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0]))
        deaths_in_30d = max(0, int(deaths_in_30d_model.predict(np.array([[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0]))

        week = d_end.isocalendar()[1] + 1
        year = d_end.year
        if week > 52:
            week = 1
            year += 1
        new_countries_next_week = max(0, int(new_countries_next_week_model.predict(np.array([[virus_id, year, week]]))[0]))

        official_dates = [date for date in all_dates if date in official_raw_data]

        official_data = {
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "new_cases": {date: official_raw_data[date]["nouveaux_cas"] for date in official_dates},
            "new_deaths": {date: official_raw_data[date]["nouveaux_deces"] for date in official_dates},
            "transmission_rate": {date: official_raw_data[date]["taux_infection"] for date in official_dates},
            "mortality_rate": {date: official_raw_data[date]["taux_mortalite"] for date in official_dates},
            "peak_date": peak_date_str,
            "estimated_duration_days": estimated_duration_days,
            "cases_in_30d": cases_in_30d,
            "deaths_in_30d": deaths_in_30d,
            "new_countries_next_week": new_countries_next_week
        }

        if dates_to_predict:
            all_new_cases = {}
            all_new_deaths = {}
            all_transmission_rate = {}
            all_mortality_rate = {}
            all_geographic_spread = {}

            for date in all_dates:
                if date in official_raw_data:
                    all_new_cases[date] = official_raw_data[date]["nouveaux_cas"]
                    all_new_deaths[date] = official_raw_data[date]["nouveaux_deces"]
                    all_transmission_rate[date] = official_raw_data[date]["taux_infection"]
                    all_mortality_rate[date] = official_raw_data[date]["taux_mortalite"]
                    d = datetime.strptime(date, "%Y-%m-%d")
                    X_geo = np.array([[virus_id, d.year]])
                    all_geographic_spread[date] = max(0, int(geographic_spread_model.predict(X_geo)[0]))
                elif date in prediction_raw_data:
                    all_new_cases[date] = prediction_raw_data[date]["nouveaux_cas"]
                    all_new_deaths[date] = prediction_raw_data[date]["nouveaux_deces"]
                    all_transmission_rate[date] = prediction_raw_data[date]["taux_infection"]
                    all_mortality_rate[date] = prediction_raw_data[date]["taux_mortalite"]
                    all_geographic_spread[date] = prediction_raw_data[date]["geographic_spread"]

            predictions_data = {
                "total_cases": total_cases,
                "total_deaths": total_deaths,
                "new_cases": all_new_cases,
                "new_deaths": all_new_deaths,
                "transmission_rate": all_transmission_rate,
                "mortality_rate": all_mortality_rate,
                "geographic_spread": all_geographic_spread,
                "peak_date": peak_date_str,
                "estimated_duration_days": estimated_duration_days,
                "cases_in_30d": cases_in_30d,
                "deaths_in_30d": deaths_in_30d,
                "new_countries_next_week": new_countries_next_week
            }
        else:
            predictions_data = {}

        result = {
            "country": country,
            "virus": virus,
            "date_start": date_start,
            "date_end": date_end,
            "official": official_data,
            "predictions": predictions_data
        }

        return result

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise