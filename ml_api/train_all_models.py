import pandas as pd
from sqlalchemy import create_engine, Column, Integer, BigInteger, Numeric, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from config import config

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


def train_and_save_model(X, y, model_path):
    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, model_path)
    print(f"Modèle sauvegardé : {model_path}")


def main():
    session = get_session()
    df = fetch_training_data(session)
    df = prepare_features(df)

    features = ["id_pays", "id_virus", "day_of_year"]

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

    print("Tous les modèles sont entraînés et sauvegardés.")


if __name__ == "__main__":
    main()
