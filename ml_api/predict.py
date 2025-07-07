import joblib
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, Table, MetaData, and_
from config import config
import logging
import os
import pickle

CACHE_PATH = "prediction_cache_{country}_{virus}.pkl"


def save_prediction_cache(country, virus, data):
    path = CACHE_PATH.format(country=country, virus=virus)
    with open(path, "wb") as f:
        pickle.dump(data, f)


def load_prediction_cache(country, virus):
    path = CACHE_PATH.format(country=country, virus=virus)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Chargement des modèles...")
try:
    new_cases_model = joblib.load("models/new_cases_model.joblib")
    new_deaths_model = joblib.load("models/new_deaths_model.joblib")
    infection_rate_model = joblib.load("models/infection_rate_model.joblib")
    mortality_rate_model = joblib.load("models/mortality_rate_model.joblib")
    total_cases_model = joblib.load("models/total_cases_model.joblib")
    total_deaths_model = joblib.load("models/total_deaths_model.joblib")
    peak_date_model = joblib.load("models/peak_date_model.joblib")
    estimated_duration_model = joblib.load(
        "models/estimated_duration_model.joblib")
    cases_in_30d_model = joblib.load("models/cases_in_30d_model.joblib")
    deaths_in_30d_model = joblib.load("models/deaths_in_30d_model.joblib")
    geographic_spread_model = joblib.load(
        "models/geographic_spread_model.joblib")
    new_countries_next_week_model = joblib.load(
        "models/new_countries_next_week_model.joblib")
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


def get_latest_data_date(country_id, virus_id):
    try:
        engine = create_engine(config.get_database_url())
        meta = MetaData()
        stats = Table('Statistiques_Journalieres', meta, autoload_with=engine)

        with engine.connect() as conn:
            query = select(stats.c.date).where(
                and_(
                    stats.c.id_pays == country_id,
                    stats.c.id_virus == virus_id
                )
            ).order_by(stats.c.date.desc()).limit(1)

            result = conn.execute(query).first()
            if result:
                return result[0]
            else:
                return None
    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération de la dernière date: {e}")
        return None


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
            logger.info(
                f"Données officielles récupérées: {len(results)} enregistrements")

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
        logger.error(
            f"Erreur lors de la récupération des données officielles: {e}")
        raise


def get_dates_to_predict(all_dates, country_id, virus_id):
    latest_data_date = get_latest_data_date(country_id, virus_id)

    if latest_data_date is None:
        # Si aucune donnée n'existe, prédire toutes les dates
        logger.info(
            "Aucune donnée historique trouvée, prédiction de toutes les dates")
        return all_dates

    logger.info(f"Dernière date avec données officielles: {latest_data_date}")

    # Filtrer pour ne garder que les dates postérieures à la dernière date en BDD
    dates_to_predict = []
    for date in all_dates:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        if date_obj > latest_data_date:
            dates_to_predict.append(date)

    logger.info(f"Dates à prédire: {len(dates_to_predict)} dates")
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

    logger.info(
        f"Génération des prédictions pour {len(dates_to_predict)} dates")
    prediction_data = {}

    for date_str in dates_to_predict:
        prediction_data[date_str] = predict_single_day(
            country_id, virus_id, date_str)

    return prediction_data


def moving_average(data_dict, window_size=7):
    """Lisse un dict {date: valeur} par moyenne glissante (sur les valeurs, garde les dates)."""
    if not data_dict:
        return {}
    dates = sorted(data_dict.keys())
    values = [data_dict[date] for date in dates]
    if len(values) < window_size:
        return dict(zip(dates, values))
    smoothed = np.convolve(values, np.ones(
        window_size)/window_size, mode='same')
    return dict(zip(dates, smoothed))


def lissage_officiel_prediction(official_dict, pred_dict, window_size=7):
    # Fusionne les deux dicts (dates triées)
    all_dates = sorted(
        set(list(official_dict.keys()) + list(pred_dict.keys())))
    all_values = []
    for date in all_dates:
        if date in official_dict:
            all_values.append(official_dict[date])
        elif date in pred_dict:
            all_values.append(pred_dict[date])
        else:
            all_values.append(0)
    # Lissage sur toute la série
    if len(all_values) < window_size:
        smoothed = all_values
    else:
        smoothed = np.convolve(all_values, np.ones(
            window_size)/window_size, mode='same')
    # Sépare à nouveau selon les dates d'origine
    liss_off = {}
    liss_pred = {}
    for i, date in enumerate(all_dates):
        if date in official_dict:
            liss_off[date] = float(smoothed[i])
        if date in pred_dict:
            liss_pred[date] = float(smoothed[i])
    return liss_off, liss_pred


def predict_pandemic(country: str, virus: str, date_start: str, date_end: str):
    """
    Calcule des prédictions pour un pays et un virus donnés sur une période.
    """
    cache = load_prediction_cache(country, virus)
    d_start = datetime.strptime(date_start, "%Y-%m-%d")
    d_end = datetime.strptime(date_end, "%Y-%m-%d")
    if cache:
        # Filtre la période demandée dans le cache
        all_dates = [(d_start + timedelta(days=i)).strftime("%Y-%m-%d")
                     for i in range((d_end - d_start).days + 1)]
        # Filtrage des données officielles et prédictions
        official = cache["official"]
        predictions = cache["predictions"]

        def filter_dict(d):
            return {k: v for k, v in d.items() if k in all_dates}
        official_filtered = official.copy()
        predictions_filtered = predictions.copy()
        for key in ["new_cases", "new_deaths", "transmission_rate", "mortality_rate"]:
            if key in official:
                official_filtered[key] = filter_dict(official[key])
            if key in predictions:
                predictions_filtered[key] = filter_dict(predictions[key])
        result = {
            "country": country,
            "virus": virus,
            "date_start": date_start,
            "date_end": date_end,
            "official": official_filtered,
            "predictions": predictions_filtered
        }
        return result
    # Si cache absent, on calcule sur 10 ans et on stocke
    d_start_10y = d_start
    d_end_10y = d_start + timedelta(days=365*10)
    result_10y = _predict_pandemic_full(country, virus, d_start_10y.strftime(
        "%Y-%m-%d"), d_end_10y.strftime("%Y-%m-%d"))
    save_prediction_cache(country, virus, result_10y)
    # Puis relance la fonction pour servir la période demandée
    return predict_pandemic(country, virus, date_start, date_end)


def _predict_pandemic_full(country: str, virus: str, date_start: str, date_end: str):
    """
    Calcule des prédictions pour un pays et un virus donnés sur une période.
    """
    try:
        # Validation des dates
        d_start = datetime.strptime(date_start, "%Y-%m-%d")
        d_end = datetime.strptime(date_end, "%Y-%m-%d")

        if d_start > d_end:
            raise ValueError(
                "La date de début doit être antérieure à la date de fin")

        nb_days = (d_end - d_start).days + 1

        # Récupération des IDs
        country_id = get_country_id(country)
        virus_id = get_virus_id(virus)

        # Génération de toutes les dates de la période
        all_dates = [(d_start + timedelta(days=i)).strftime("%Y-%m-%d")
                     for i in range(nb_days)]

        # Récupération des données officielles
        official_raw_data = get_official_data(
            country_id, virus_id, date_start, date_end)

        # Identification des dates à prédire
        dates_to_predict = get_dates_to_predict(
            all_dates, country_id, virus_id)

        # Génération des prédictions uniquement pour les dates nécessaires
        prediction_raw_data = generate_predictions(
            country_id, virus_id, dates_to_predict)

        total_cases = max(0, int(total_cases_model.predict(
            np.array([[country_id, virus_id, d_end.year, d_end.timetuple().tm_yday]]))[0]))
        total_deaths = max(0, int(total_deaths_model.predict(
            np.array([[country_id, virus_id, d_end.year, d_end.timetuple().tm_yday]]))[0]))

        peak_day_of_year = int(peak_date_model.predict(np.array(
            [[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0])
        peak_date = datetime(d_start.year, 1, 1) + \
            timedelta(days=peak_day_of_year - 1)
        peak_date_str = peak_date.strftime("%Y-%m-%d")

        estimated_duration_days = max(1, int(estimated_duration_model.predict(np.array(
            [[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0]))
        cases_in_30d = max(0, int(cases_in_30d_model.predict(np.array(
            [[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0]))
        deaths_in_30d = max(0, int(deaths_in_30d_model.predict(np.array(
            [[country_id, virus_id, d_start.year, d_start.timetuple().tm_yday]]))[0]))

        week = d_end.isocalendar()[1] + 1
        year = d_end.year
        if week > 52:
            week = 1
            year += 1
        new_countries_next_week = max(0, int(
            new_countries_next_week_model.predict(np.array([[virus_id, year, week]]))[0]))

        official_dates = [
            date for date in all_dates if date in official_raw_data]

        # Construction des dicts pour lissage fusionné
        dict_new_cases_off = {
            date: official_raw_data[date]["nouveaux_cas"] for date in official_dates}
        dict_new_deaths_off = {
            date: official_raw_data[date]["nouveaux_deces"] for date in official_dates}
        dict_transmission_off = {
            date: official_raw_data[date]["taux_infection"] for date in official_dates}
        dict_mortality_off = {
            date: official_raw_data[date]["taux_mortalite"] for date in official_dates}

        if dates_to_predict:
            all_new_cases = {}
            all_new_deaths = {}
            all_transmission_rate = {}
            all_mortality_rate = {}
            all_geographic_spread = {}

            for date in dates_to_predict:
                if date in prediction_raw_data:
                    all_new_cases[date] = prediction_raw_data[date]["nouveaux_cas"]
                    all_new_deaths[date] = prediction_raw_data[date]["nouveaux_deces"]
                    all_transmission_rate[date] = prediction_raw_data[date]["taux_infection"]
                    all_mortality_rate[date] = prediction_raw_data[date]["taux_mortalite"]
                    d = datetime.strptime(date, "%Y-%m-%d")
                    X_geo = np.array([[virus_id, d.year]])
                    all_geographic_spread[date] = max(
                        0, int(geographic_spread_model.predict(X_geo)[0]))
                elif date in prediction_raw_data:
                    all_new_cases[date] = prediction_raw_data[date]["nouveaux_cas"]
                    all_new_deaths[date] = prediction_raw_data[date]["nouveaux_deces"]
                    all_transmission_rate[date] = prediction_raw_data[date]["taux_infection"]
                    all_mortality_rate[date] = prediction_raw_data[date]["taux_mortalite"]
                    all_geographic_spread[date] = prediction_raw_data[date]["geographic_spread"]

            # Lissage fusionné puis séparation
            liss_new_cases_off, liss_new_cases_pred = lissage_officiel_prediction(
                dict_new_cases_off, all_new_cases)
            liss_new_deaths_off, liss_new_deaths_pred = lissage_officiel_prediction(
                dict_new_deaths_off, all_new_deaths)
            liss_transmission_off, liss_transmission_pred = lissage_officiel_prediction(
                dict_transmission_off, all_transmission_rate)
            liss_mortality_off, liss_mortality_pred = lissage_officiel_prediction(
                dict_mortality_off, all_mortality_rate)

            official_data = {
                "total_cases": total_cases,
                "total_deaths": total_deaths,
                "new_cases": liss_new_cases_off,
                "new_deaths": liss_new_deaths_off,
                "transmission_rate": liss_transmission_off,
                "mortality_rate": liss_mortality_off,
                "peak_date": peak_date_str,
                "estimated_duration_days": estimated_duration_days,
                "cases_in_30d": cases_in_30d,
                "deaths_in_30d": deaths_in_30d,
                "new_countries_next_week": new_countries_next_week
            }

            predictions_data = {
                "total_cases": total_cases,
                "total_deaths": total_deaths,
                "new_cases": liss_new_cases_pred,
                "new_deaths": liss_new_deaths_pred,
                "transmission_rate": liss_transmission_pred,
                "mortality_rate": liss_mortality_pred,
                "geographic_spread": all_geographic_spread,
                "peak_date": peak_date_str,
                "estimated_duration_days": estimated_duration_days,
                "cases_in_30d": cases_in_30d,
                "deaths_in_30d": deaths_in_30d,
                "new_countries_next_week": new_countries_next_week
            }
        else:
            # Pas de prédiction, lissage classique sur officiel
            official_data = {
                "total_cases": total_cases,
                "total_deaths": total_deaths,
                "new_cases": moving_average(dict_new_cases_off),
                "new_deaths": moving_average(dict_new_deaths_off),
                "transmission_rate": moving_average(dict_transmission_off),
                "mortality_rate": moving_average(dict_mortality_off),
                "peak_date": peak_date_str,
                "estimated_duration_days": estimated_duration_days,
                "cases_in_30d": cases_in_30d,
                "deaths_in_30d": deaths_in_30d,
                "new_countries_next_week": new_countries_next_week
            }
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
