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
peak_date_model = joblib.load("models/peak_date_model.joblib")
estimated_duration_model = joblib.load(
    "models/estimated_duration_model.joblib")
cases_in_30d_model = joblib.load("models/cases_in_30d_model.joblib")
deaths_in_30d_model = joblib.load("models/deaths_in_30d_model.joblib")
geographic_spread_model = joblib.load("models/geographic_spread_model.joblib")
new_countries_next_week_model = joblib.load(
    "models/new_countries_next_week_model.joblib")


def model_new_cases(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        year = (d + timedelta(days=i)).year
        day_of_year = (d + timedelta(days=i)).timetuple().tm_yday
        X = np.array([[country_id, virus_id, year, day_of_year]])
        preds.append(int(new_cases_model.predict(X)[0]))
    return preds


def model_new_deaths(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        date_i = d + timedelta(days=i)
        year = date_i.year
        day_of_year = date_i.timetuple().tm_yday
        X = np.array([[country_id, virus_id, year, day_of_year]])
        preds.append(int(new_deaths_model.predict(X)[0]))
    return preds


def model_transmission_rate(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        date_i = d + timedelta(days=i)
        year = date_i.year
        day_of_year = date_i.timetuple().tm_yday
        X = np.array([[country_id, virus_id, year, day_of_year]])
        preds.append(float(infection_rate_model.predict(X)[0]))
    return preds


def model_mortality_rate(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        date_i = d + timedelta(days=i)
        year = date_i.year
        day_of_year = date_i.timetuple().tm_yday
        X = np.array([[country_id, virus_id, year, day_of_year]])
        preds.append(float(mortality_rate_model.predict(X)[0]))
    return preds


def model_total_cases(country_id, virus_id, date):
    d = datetime.strptime(date, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, year, day_of_year]])
    return int(total_cases_model.predict(X)[0])


def model_total_deaths(country_id, virus_id, date):
    d = datetime.strptime(date, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, year, day_of_year]])
    return int(total_deaths_model.predict(X)[0])


def model_geographic_spread(country_id, virus_id, date_start, nb_days):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    preds = []
    for i in range(nb_days):
        year = (d + timedelta(days=i)).year
        X = np.array([[virus_id, year]])
        preds.append(int(geographic_spread_model.predict(X)[0]))
    return preds


def model_peak_date(country_id, virus_id, date_start):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, year, day_of_year]])
    # Le modèle prédit le jour de l'année du pic
    peak_day_of_year = int(peak_date_model.predict(X)[0])
    peak_date = datetime(year, 1, 1) + timedelta(days=peak_day_of_year - 1)
    return peak_date.strftime("%Y-%m-%d")


def model_estimated_duration(country_id, virus_id, date_start):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, year, day_of_year]])
    return int(estimated_duration_model.predict(X)[0])


def model_cases_in_30d(country_id, virus_id, date_start):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, year, day_of_year]])
    return int(cases_in_30d_model.predict(X)[0])


def model_deaths_in_30d(country_id, virus_id, date_start):
    d = datetime.strptime(date_start, "%Y-%m-%d")
    year = d.year
    day_of_year = d.timetuple().tm_yday
    X = np.array([[country_id, virus_id, year, day_of_year]])
    return int(deaths_in_30d_model.predict(X)[0])


def model_new_countries_next_week(country_id, virus_id, date_end):
    d = datetime.strptime(date_end, "%Y-%m-%d")
    year = d.year
    week = d.isocalendar()[1] + 1
    if week > 52:
        week = 1
        year += 1
    X = np.array([[virus_id, year, week]])
    value = int(new_countries_next_week_model.predict(X)[0])
    value = max(0, value)
    return value


def predict_pandemic(country: str, virus: str, date_start: str, date_end: str):
    """
    Calcule des prédictions pour un pays et un virus donnés sur une période.
    """
    country_id = get_country_id(country)
    virus_id = get_virus_id(virus)
    d_start = datetime.strptime(date_start, "%Y-%m-%d")
    nb_days = (datetime.strptime(date_end, "%Y-%m-%d") - d_start).days + 1

    new_cases = model_new_cases(country_id, virus_id, date_start, nb_days)
    new_deaths = model_new_deaths(country_id, virus_id, date_start, nb_days)
    transmission_rate = model_transmission_rate(
        country_id, virus_id, date_start, nb_days)
    mortality_rate = model_mortality_rate(
        country_id, virus_id, date_start, nb_days)
    total_cases = model_total_cases(country_id, virus_id, date_end)
    total_deaths = model_total_deaths(country_id, virus_id, date_end)
    geographic_spread = model_geographic_spread(
        country_id, virus_id, date_start, nb_days)
    peak_date = model_peak_date(country_id, virus_id, date_start)
    estimated_duration_days = model_estimated_duration(
        country_id, virus_id, date_start)
    cases_in_30d = model_cases_in_30d(country_id, virus_id, date_start)
    deaths_in_30d = model_deaths_in_30d(country_id, virus_id, date_start)
    new_countries_next_week = model_new_countries_next_week(
        country_id, virus_id, date_end)

    dates = [(d_start + timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(nb_days)]

    def to_date_dict(values):
        return {date: value for date, value in zip(dates, values)}

    return {
        "country": country,
        "virus": virus,
        "date_start": date_start,
        "date_end": date_end,
        "predictions": {
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "new_cases": to_date_dict(new_cases),
            "new_deaths": to_date_dict(new_deaths),
            "transmission_rate": to_date_dict(transmission_rate),
            "mortality_rate": to_date_dict(mortality_rate),
            "geographic_spread": to_date_dict(geographic_spread),
            "peak_date": peak_date,
            "estimated_duration_days": estimated_duration_days,
            "cases_in_30d": cases_in_30d,
            "deaths_in_30d": deaths_in_30d,
            "new_countries_next_week": new_countries_next_week
        }
    }
