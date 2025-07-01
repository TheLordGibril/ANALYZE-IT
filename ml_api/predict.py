import joblib
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, Table, MetaData
from config import config


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


new_cases_model = joblib.load("models/new_cases_model.joblib")
new_deaths_model = joblib.load("models/new_deaths_model.joblib")
infection_rate_model = joblib.load("models/infection_rate_model.joblib")
mortality_rate_model = joblib.load("models/mortality_rate_model.joblib")
total_cases_model = joblib.load("models/total_cases_model.joblib")
total_deaths_model = joblib.load("models/total_deaths_model.joblib")


def model_new_cases(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        day_of_year = (d + timedelta(days=i)).timetuple().tm_yday
        X = np.array([[country_id, virus_id, day_of_year]])
        preds.append(int(new_cases_model.predict(X)[0]))
    return preds


def model_new_deaths(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        day_of_year = (d + timedelta(days=i)).timetuple().tm_yday
        X = np.array([[country_id, virus_id, day_of_year]])
        preds.append(int(new_deaths_model.predict(X)[0]))
    return preds


def model_transmission_rate(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        day_of_year = (d + timedelta(days=i)).timetuple().tm_yday
        X = np.array([[country_id, virus_id, day_of_year]])
        preds.append(float(infection_rate_model.predict(X)[0]))
    return preds


def model_mortality_rate(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        day_of_year = (d + timedelta(days=i)).timetuple().tm_yday
        X = np.array([[country_id, virus_id, day_of_year]])
        preds.append(float(mortality_rate_model.predict(X)[0]))
    return preds


def model_total_cases(country_id, virus_id, date):
    d = datetime.strptime(date, "%Y-%m-%d")
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, day_of_year]])
    return int(total_cases_model.predict(X)[0])


def model_total_deaths(country_id, virus_id, date):
    d = datetime.strptime(date, "%Y-%m-%d")
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, day_of_year]])
    return int(total_deaths_model.predict(X)[0])


def predict_pandemic(country: str, virus: str, date_start: str, date_end: str):
    """
    Calcule des prédictions pour un pays et un virus donnés sur une période.
    """
    country_id = get_country_id(country)
    virus_id = get_virus_id(virus)
    d_start = datetime.strptime(date_start, "%Y-%m-%d")
    d_end = datetime.strptime(date_end, "%Y-%m-%d")
    nb_days = (d_end - d_start).days + 1

    new_cases = model_new_cases(country_id, virus_id, date_start, nb_days)
    new_deaths = model_new_deaths(country_id, virus_id, date_start, nb_days)
    transmission_rate = model_transmission_rate(
        country_id, virus_id, date_start, nb_days)
    mortality_rate = model_mortality_rate(
        country_id, virus_id, date_start, nb_days)
    total_cases = model_total_cases(country_id, virus_id, date_end)
    total_deaths = model_total_deaths(country_id, virus_id, date_end)

    # geographic_spread = model_geographic_spread(country, virus, date)
    # peak_date = model_peak_date(country, virus, date)
    # estimated_duration_days = model_estimated_duration(country, virus, date)
    # cases_in_30d = model_cases_in_30d(country, virus, date)
    # deaths_in_30d = model_deaths_in_30d(country, virus, date)
    # new_countries_next_week = model_new_countries_next_week(
    #     country, virus, date)

    # Calcul des totaux cumulés (exemple simple)

    return {
        "country": country,
        "virus": virus,
        "predictions": {
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "new_cases": new_cases,
            "new_deaths": new_deaths,
            "transmission_rate": transmission_rate,
            "mortality_rate": mortality_rate,
            # "geographic_spread": geographic_spread,
            # "peak_date": peak_date,
            # "estimated_duration_days": estimated_duration_days,
            # "cases_in_30d": cases_in_30d,
            # "deaths_in_30d": deaths_in_30d,
            # "new_countries_next_week": new_countries_next_week
        }
    }
