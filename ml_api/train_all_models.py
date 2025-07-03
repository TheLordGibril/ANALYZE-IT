import pandas as pd
from sqlalchemy import create_engine, Column, Integer, BigInteger, Numeric, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from config import config
from xgboost import XGBRegressor

# Redéfinition des modèles SQLAlchemy nécessaires
Base = declarative_base()


class StatistiquesJournalieres(Base):
    __tablename__ = "Statistiques_Journalieres"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_pays = Column(Integer, nullable=False)
    id_virus = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    nouveaux_cas = Column(Integer, nullable=True)
    nouveaux_deces = Column(Integer, nullable=True)
    taux_infection = Column(Numeric, nullable=True)
    taux_mortalite = Column(Numeric, nullable=True)
    total_cas = Column(Integer, nullable=True)
    total_deces = Column(Integer, nullable=True)


def get_session():
    engine = create_engine(config.get_database_url(), echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def fetch_training_data(session):
    query = session.query(
        StatistiquesJournalieres.id_pays,
        StatistiquesJournalieres.id_virus,
        StatistiquesJournalieres.date,
        StatistiquesJournalieres.nouveaux_cas,
        StatistiquesJournalieres.nouveaux_deces,
        StatistiquesJournalieres.taux_infection,
        StatistiquesJournalieres.taux_mortalite,
        StatistiquesJournalieres.total_cas,
        StatistiquesJournalieres.total_deces
    )
    df = pd.read_sql(query.statement, session.bind)
    return df


def prepare_features(df):
    df["day_of_year"] = df["date"].apply(lambda d: d.timetuple().tm_yday)
    return df


def train_and_save_model(X, y, model_path, use_xgb=False):
    if use_xgb:
        model = XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1
        )
    else:
        model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, model_path)
    print(f"Modèle sauvegardé : {model_path}")


def main():
    session = get_session()
    df = fetch_training_data(session)
    df = prepare_features(df)

    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    features = ["id_pays", "id_virus", "year", "day_of_year"]

    X_cases = df[features].values
    y_cases = df["nouveaux_cas"].values
    train_and_save_model(X_cases, y_cases, "models/new_cases_model.joblib")

    y_deaths = df["nouveaux_deces"].values
    train_and_save_model(X_cases, y_deaths, "models/new_deaths_model.joblib")

    y_infection = df["taux_infection"].fillna(0).values
    train_and_save_model(X_cases, y_infection,
                         "models/infection_rate_model.joblib")

    y_mortalite = df["taux_mortalite"].fillna(0).values
    train_and_save_model(X_cases, y_mortalite,
                         "models/mortality_rate_model.joblib")

    y_total_cases = df["total_cas"].values
    train_and_save_model(X_cases, y_total_cases,
                         "models/total_cases_model.joblib")

    y_total_deaths = df["total_deces"].values
    train_and_save_model(X_cases, y_total_deaths,
                         "models/total_deaths_model.joblib")

    df["date"] = pd.to_datetime(df["date"])
    df['year'] = df['date'].dt.year
    peak_days = (
        df.groupby(['id_pays', 'id_virus', 'year'])[
            ['nouveaux_cas', 'day_of_year']]
        .apply(lambda g: g.loc[g['nouveaux_cas'].idxmax(), 'day_of_year'])
        .reset_index(name='peak_day_of_year')
    )
    df_peak = pd.merge(df, peak_days, on=['id_pays', 'id_virus', 'year'])
    X_peak = df_peak[["id_pays", "id_virus", "year", "day_of_year"]].values
    y_peak = df_peak["peak_day_of_year"].values
    train_and_save_model(X_peak, y_peak, "models/peak_date_model.joblib")

    duration = (
        df[df['nouveaux_cas'] > 0]
        .groupby(['id_pays', 'id_virus', 'year'])['day_of_year']
        .agg(['min', 'max'])
        .reset_index()
    )
    duration['duration'] = duration['max'] - duration['min'] + 1
    df_duration = pd.merge(df, duration, on=['id_pays', 'id_virus', 'year'])
    X_duration = df_duration[["id_pays",
                              "id_virus", "year", "day_of_year"]].values
    y_duration = df_duration["duration"].values
    train_and_save_model(X_duration, y_duration,
                         "models/estimated_duration_model.joblib")

    df = df.sort_values(['id_pays', 'id_virus', 'date'])
    df['cases_in_30d'] = df.groupby(['id_pays', 'id_virus'])['nouveaux_cas'].transform(
        lambda x: x.rolling(
            window=30, min_periods=1).sum().shift(-29).fillna(0)
    )
    df['deaths_in_30d'] = df.groupby(['id_pays', 'id_virus'])['nouveaux_deces'].transform(
        lambda x: x.rolling(
            window=30, min_periods=1).sum().shift(-29).fillna(0)
    )
    X_30d = df[features].values
    y_cases_30d = df["cases_in_30d"].values
    y_deaths_30d = df["deaths_in_30d"].values
    train_and_save_model(X_30d, y_cases_30d,
                         "models/cases_in_30d_model.joblib", use_xgb=True)
    train_and_save_model(X_30d, y_deaths_30d,
                         "models/deaths_in_30d_model.joblib", use_xgb=True)

    df['cases_in_7d'] = df.groupby(['id_pays', 'id_virus'])['nouveaux_cas'].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum().shift(-6).fillna(0)
    )
    df['deaths_in_7d'] = df.groupby(['id_pays', 'id_virus'])['nouveaux_deces'].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum().shift(-6).fillna(0)
    )
    X_7d = df[features].values
    y_cases_7d = df["cases_in_7d"].values
    y_deaths_7d = df["deaths_in_7d"].values
    train_and_save_model(X_7d, y_cases_7d, "models/cases_in_7d_model.joblib")
    train_and_save_model(X_7d, y_deaths_7d, "models/deaths_in_7d_model.joblib")

    geo_spread = (
        df.groupby(['id_virus', 'year'])['id_pays']
        .nunique()
        .reset_index(name='num_countries_affected')
    )
    X_geo = geo_spread[["id_virus", "year"]].values
    y_geo = geo_spread["num_countries_affected"].values
    train_and_save_model(X_geo, y_geo, "models/geographic_spread_model.joblib")

    df = df.sort_values(['id_virus', 'id_pays', 'date'])
    df['first_case'] = df.groupby(['id_virus', 'id_pays'])[
        'date'].transform('min')
    df['week'] = df['date'].dt.isocalendar().week
    new_countries_week = (
        df[df['date'] == df['first_case']]
        .groupby(['id_virus', 'year', 'week'])['id_pays']
        .count()
        .reset_index(name='new_countries')
    )
    X_new_countries = new_countries_week[["id_virus", "year", "week"]].values
    y_new_countries = new_countries_week["new_countries"].values
    train_and_save_model(X_new_countries, y_new_countries,
                         "models/new_countries_next_week_model.joblib")

    print("Tous les modèles sont entraînés et sauvegardés.")


if __name__ == "__main__":
    main()
