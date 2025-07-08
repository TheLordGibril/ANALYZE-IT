import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Numeric, Date
from sqlalchemy.orm import declarative_base, sessionmaker
import numpy as np
from config import config
from model_comparison import ModelComparison
import os
import warnings

warnings.filterwarnings('ignore')

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
    # Convertir la date si ce n'est pas déjà fait
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    # Features temporelles de base
    df["day_of_year"] = df["date"].dt.dayofyear
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["week"] = df["date"].dt.isocalendar().week

    print("   Tri des données...")
    # Trier par pays, virus et date pour les calculs de tendance
    df = df.sort_values(['id_pays', 'id_virus', 'date']).reset_index(drop=True)

    print("   Calcul des features de tendance...")

    # Méthode robuste pour les features de tendance
    def calculate_rolling_features(group):
        group = group.sort_values('date').reset_index(drop=True)

        # Lag features
        group['cases_lag_7'] = group['nouveaux_cas'].shift(7).fillna(0)

        # Rolling means (avec gestion des groupes de petite taille)
        window_size = min(7, len(group))
        group['cases_rolling_7'] = group['nouveaux_cas'].rolling(
            window=window_size, min_periods=1, center=False
        ).mean().fillna(group['nouveaux_cas'])

        group['deaths_rolling_7'] = group['nouveaux_deces'].rolling(
            window=window_size, min_periods=1, center=False
        ).mean().fillna(group['nouveaux_deces'])

        # Taux de croissance
        group['growth_rate'] = group['nouveaux_cas'].pct_change().fillna(0)

        # Remplacer les valeurs infinies par 0
        group['growth_rate'] = group['growth_rate'].replace(
            [np.inf, -np.inf], 0)

        return group

    # Appliquer les calculs par groupe avec gestion d'erreur
    try:
        tqdm_disabled = True  # Désactiver la barre de progression pour éviter les conflits
        df = df.groupby(['id_pays', 'id_virus'], group_keys=False).apply(
            calculate_rolling_features)
        df = df.reset_index(drop=True)

        print(f"   ✅ Features de tendance ajoutées avec succès")
        print(f"   Features disponibles: {list(df.columns)}")

    except Exception as e:
        print(f"   ⚠️ Erreur lors du calcul des features de tendance: {e}")
        print(f"   Utilisation des features de base uniquement")
        # En cas d'erreur, on garde au moins les features temporelles
        df['cases_lag_7'] = 0
        df['cases_rolling_7'] = df['nouveaux_cas']
        df['deaths_rolling_7'] = df['nouveaux_deces']
        df['growth_rate'] = 0

    print(f"   Forme finale du DataFrame: {df.shape}")
    return df


def create_models_directory():
    if not os.path.exists('models'):
        os.makedirs('models')
        print("📁 Répertoire 'models' créé")
    else:
        print("📁 Répertoire 'models' existe déjà")


def safe_train_model(comparator, X, y, model_name, save_path, min_samples=100):
    """Entraîne un modèle de manière sécurisée"""
    try:
        # Vérifier qu'il y a assez de données
        if len(X) < min_samples:
            print(
                f"   ⚠️ Pas assez de données ({len(X)} < {min_samples}). Modèle {model_name} ignoré.")
            return False

        # Vérifier qu'il n'y a pas que des zéros
        if np.all(y == 0):
            print(
                f"   ⚠️ Toutes les valeurs cibles sont nulles. Modèle {model_name} ignoré.")
            return False

        # Vérifier qu'il y a de la variance dans les données
        if np.var(y) == 0:
            print(
                f"   ⚠️ Aucune variance dans les données cibles. Modèle {model_name} ignoré.")
            return False

        # Entraîner le modèle
        comparator.compare_algorithms(X, y, model_name)
        success = comparator.save_best_model(model_name, save_path)

        if success:
            print(
                f"   ✅ Modèle {model_name} entraîné et sauvegardé avec succès")
            return True
        else:
            print(f"   ❌ Échec de la sauvegarde du modèle {model_name}")
            return False

    except Exception as e:
        print(f"   ❌ Erreur lors de l'entraînement de {model_name}: {str(e)}")
        return False


def main():
    create_models_directory()
    session = get_session()
    df = fetch_training_data(session)
    df = prepare_features(df)

    df["date"] = pd.to_datetime(df["date"])
    df["day_of_year"] = df["date"].dt.dayofyear
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # Initialisation du comparateur
    comparator = ModelComparison()

    # Définition des features à utiliser
    basic_features = ["id_pays", "id_virus", "year", "day_of_year"]

    # Vérifier quelles features sont disponibles
    available_columns = df.columns.tolist()
    advanced_features = basic_features.copy()

    features_to_use = advanced_features

    # Préparer les données principales
    X_main = df[features_to_use].fillna(0).values

    # ENTRAÎNEMENT DES MODÈLES PRINCIPAUX
    models_to_train = [
        ("Nouveaux Cas", "nouveaux_cas", "models/new_cases_model.joblib"),
        ("Nouveaux Décès", "nouveaux_deces", "models/new_deaths_model.joblib"),
        ("Taux Infection", "taux_infection", "models/infection_rate_model.joblib"),
        ("Taux Mortalité", "taux_mortalite", "models/mortality_rate_model.joblib"),
        ("Total Cas", "total_cas", "models/total_cases_model.joblib"),
        ("Total Décès", "total_deces", "models/total_deaths_model.joblib")
    ]

    trained_models = 0
    for model_name, column_name, save_path in models_to_train:
        print(f"Entraînement: {model_name}")

        if column_name in df.columns:
            y = df[column_name].fillna(0).values
            success = safe_train_model(
                comparator, X_main, y, model_name, save_path)
            if success:
                trained_models += 1

    # ENTRAÎNEMENT DES MODÈLES COMPLEXES
    # 1. MODÈLE DATE DE PIC
    print(f"Calcul des dates de pic...")
    try:
        # Calculer les pics de manière plus robuste
        peak_data = []

        for (pays, virus, year), group in df.groupby(['id_pays', 'id_virus', 'year']):
            if len(group) > 0 and group['nouveaux_cas'].max() > 0:
                peak_idx = group['nouveaux_cas'].idxmax()
                peak_day = group.loc[peak_idx, 'day_of_year']
                peak_data.append({
                    'id_pays': pays,
                    'id_virus': virus,
                    'year': year,
                    'peak_day_of_year': peak_day
                })

        if len(peak_data) >= 50:
            peak_df = pd.DataFrame(peak_data)
            df_peak = pd.merge(
                df, peak_df, on=['id_pays', 'id_virus', 'year'], how='inner')

            if len(df_peak) > 0:
                X_peak = df_peak[basic_features].values
                y_peak = df_peak["peak_day_of_year"].values
                safe_train_model(comparator, X_peak, y_peak,
                                 "Date Pic", "models/peak_date_model.joblib", 50)
            else:
                print("Aucune donnée après merge pour les dates de pic.")
        else:
            print(
                f"Pas assez de données pour les dates de pic ({len(peak_data)} < 50).")

    except Exception as e:
        print(f"Erreur calcul date de pic: {e}")

    # 2. MODÈLE DURÉE ESTIMÉE
    print(f"\nCalcul des durées estimées...")
    try:
        duration_data = []

        for (pays, virus, year), group in df.groupby(['id_pays', 'id_virus', 'year']):
            cases_data = group[group['nouveaux_cas'] > 0]
            if len(cases_data) > 1:
                min_day = cases_data['day_of_year'].min()
                max_day = cases_data['day_of_year'].max()
                duration = max_day - min_day + 1
                duration_data.append({
                    'id_pays': pays,
                    'id_virus': virus,
                    'year': year,
                    'duration': duration
                })

        if len(duration_data) >= 50:
            duration_df = pd.DataFrame(duration_data)
            df_duration = pd.merge(df, duration_df, on=[
                                   'id_pays', 'id_virus', 'year'], how='inner')

            if len(df_duration) > 0:
                X_duration = df_duration[basic_features].values
                y_duration = df_duration["duration"].values
                safe_train_model(comparator, X_duration, y_duration, "Durée Estimée",
                                 "models/estimated_duration_model.joblib", 50)
            else:
                print("Aucune donnée après merge pour les durées.")
        else:
            print(
                f"Pas assez de données pour les durées ({len(duration_data)} < 50).")

    except Exception as e:
        print(f"Erreur calcul durée: {e}")

    # 3. MODÈLES PRÉDICTIONS 30 JOURS
    print(f"\nCalcul des prédictions 30 jours...")
    try:
        df_sorted = df.sort_values(
            ['id_pays', 'id_virus', 'date']).reset_index(drop=True)

        # Calcul simplifié et robuste des sommes sur 30 jours
        def calculate_rolling_predictions(group):
            group = group.sort_values('date').reset_index(drop=True)

            # Fenêtres de 30 jours
            window_30 = min(30, len(group))
            group['cases_in_30d'] = group['nouveaux_cas'].rolling(
                window=window_30, min_periods=1
            ).sum()
            group['deaths_in_30d'] = group['nouveaux_deces'].rolling(
                window=window_30, min_periods=1
            ).sum()

            return group

        df_rolling = df_sorted.groupby(['id_pays', 'id_virus'], group_keys=False).apply(
            calculate_rolling_predictions)
        df_rolling = df_rolling.reset_index(drop=True)

        X_rolling = df_rolling[basic_features].values

        # Modèles 30 jours
        y_cases_30d = df_rolling["cases_in_30d"].values
        y_deaths_30d = df_rolling["deaths_in_30d"].values
        safe_train_model(comparator, X_rolling, y_cases_30d,
                         "Cas 30 Jours", "models/cases_in_30d_model.joblib")
        safe_train_model(comparator, X_rolling, y_deaths_30d,
                         "Décès 30 Jours", "models/deaths_in_30d_model.joblib")

    except Exception as e:
        print(f"Erreur calcul prédictions rolling: {e}")

    # 4. MODÈLE PROPAGATION GÉOGRAPHIQUE
    print(f"\nCalcul de la propagation géographique...")
    try:
        geo_spread = (
            df.groupby(['id_virus', 'year'])['id_pays']
            .nunique()
            .reset_index(name='num_countries_affected')
        )

        if len(geo_spread) >= 20:
            X_geo = geo_spread[["id_virus", "year"]].values
            y_geo = geo_spread["num_countries_affected"].values
            safe_train_model(comparator, X_geo, y_geo, "Propagation Géographique",
                             "models/geographic_spread_model.joblib", 20)
        else:
            print(
                f"Pas assez de données pour la propagation géographique ({len(geo_spread)} < 20).")

    except Exception as e:
        print(f"Erreur propagation géographique: {e}")

    # 5. MODÈLE NOUVEAUX PAYS SEMAINE SUIVANTE
    print(f"\nCalcul des nouveaux pays par semaine...")
    try:
        # Calculer la première occurrence de chaque virus par pays
        first_cases = df.groupby(['id_virus', 'id_pays'])[
            'date'].min().reset_index()
        first_cases.columns = ['id_virus', 'id_pays', 'first_case_date']
        first_cases['year'] = first_cases['first_case_date'].dt.year
        first_cases['week'] = first_cases['first_case_date'].dt.isocalendar().week

        # Compter les nouveaux pays par semaine
        new_countries_week = (
            first_cases.groupby(['id_virus', 'year', 'week'])['id_pays']
            .count()
            .reset_index(name='new_countries')
        )

        if len(new_countries_week) >= 20:
            X_new_countries = new_countries_week[[
                "id_virus", "year", "week"]].values
            y_new_countries = new_countries_week["new_countries"].values
            safe_train_model(comparator, X_new_countries, y_new_countries, "Nouveaux Pays Semaine",
                             "models/new_countries_next_week_model.joblib", 20)
        else:
            print(
                f"Pas assez de données pour les nouveaux pays ({len(new_countries_week)} < 20).")

    except Exception as e:
        print(f"Erreur nouveaux pays: {e}")

    comparator.generate_comparison_report()


if __name__ == "__main__":
    main()
