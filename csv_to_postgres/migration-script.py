import pandas as pd
from sqlalchemy import create_engine, MetaData, Column, Integer, BigInteger, Numeric, String, Date, ForeignKey, UniqueConstraint, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

from config import config
from validator import validator

# Définition des modèles SQLAlchemy
Base = declarative_base()

class MigrationStatus(Base):
    __tablename__ = "Migration_Status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), unique=True, nullable=False)
    checksum = Column(String(64), nullable=False)
    migrated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='completed')

    def __repr__(self):
        return f"<MigrationStatus(filename={self.filename}, status={self.status})>"

class User(Base):
    __tablename__ = "Users"

    id_user = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=True)
    prenom = Column(String(100), nullable=True)
    role = Column(String(20), default='USER', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id_user={self.id_user}, email={self.email}, role={self.role})>"

class Pays(Base):
    __tablename__ = "Pays"

    id_pays = Column(Integer, primary_key=True, autoincrement=True)
    nom_pays = Column(String(100), unique=True, nullable=False)
    population = Column(BigInteger, nullable=True)

    statistiques = relationship("StatistiquesJournalieres", back_populates="pays")

    def __repr__(self):
        return f"<Pays(id_pays={self.id_pays}, nom_pays={self.nom_pays}, population={self.population})>"

class Virus(Base):
    __tablename__ = "Virus"

    id_virus = Column(Integer, primary_key=True, autoincrement=True)
    nom_virus = Column(String(50), unique=True, nullable=False)

    statistiques = relationship("StatistiquesJournalieres", back_populates="virus")

    def __repr__(self):
        return f"<Virus(id_virus={self.id_virus}, nom_virus={self.nom_virus})>"

class Saisons(Base):
    __tablename__ = "Saisons"

    id_saison = Column(Integer, primary_key=True, autoincrement=True)
    nom_saison = Column(String(20), unique=True, nullable=False)

    statistiques = relationship("StatistiquesJournalieres", back_populates="saison")

    def __repr__(self):
        return f"<Saisons(id_saison={self.id_saison}, nom_saison={self.nom_saison})>"

class StatistiquesJournalieres(Base):
    __tablename__ = "Statistiques_Journalieres"

    id_stat = Column(Integer, primary_key=True, autoincrement=True)
    id_pays = Column(Integer, ForeignKey("Pays.id_pays"), nullable=False)
    id_virus = Column(Integer, ForeignKey("Virus.id_virus"), nullable=False)
    id_saison = Column(Integer, ForeignKey("Saisons.id_saison"), nullable=True)
    date = Column(Date, nullable=False)
    nouveaux_cas = Column(Integer, default=0, nullable=False)
    nouveaux_deces = Column(Integer, default=0, nullable=False)
    total_cas = Column(Integer, default=0, nullable=False)
    total_deces = Column(Integer, default=0, nullable=False)
    croissance_cas = Column(Numeric(10, 4), nullable=True)
    taux_mortalite = Column(Numeric(10, 4), nullable=True)
    taux_infection = Column(Numeric(10, 4), nullable=True)
    taux_mortalite_population = Column(Numeric(10, 4), nullable=True)
    taux_infection_vs_global = Column(Numeric(10, 4), nullable=True)
    taux_mortalite_pop_vs_global = Column(Numeric(10, 4), nullable=True)


    # Relations
    pays = relationship("Pays", back_populates="statistiques")
    virus = relationship("Virus", back_populates="statistiques")
    saison = relationship("Saisons", back_populates="statistiques")

    # Contrainte d'unicité composée
    __table_args__ = (
        UniqueConstraint('id_pays', 'id_virus', 'date', name='Statistiques_Journalieres_id_pays_id_virus_date_key'),
    )

    def __repr__(self):
        return f"<StatistiquesJournalieres(id_stat={self.id_stat}, date={self.date}, pays={self.id_pays}, virus={self.id_virus})>"

class StatistiquesGlobales(Base):
    __tablename__ = "Statistiques_Globales"

    id_global = Column(Integer, primary_key=True, autoincrement=True)
    id_virus = Column(Integer, ForeignKey("Virus.id_virus"), nullable=False)
    date = Column(Date, nullable=False)

    taux_infection_global_moyen = Column(Numeric(10, 4), nullable=True)
    taux_mortalite_pop_global_moyen = Column(Numeric(10, 4), nullable=True)
    total_cas_mondial = Column(BigInteger, nullable=True)
    total_deces_mondial = Column(BigInteger, nullable=True)

    virus = relationship("Virus")

    __table_args__ = (
        UniqueConstraint('id_virus', 'date', name='Statistiques_Globales_id_virus_date_key'),
    )

    def __repr__(self):
        return f"<StatistiquesGlobales(id_global={self.id_global}, date={self.date}, virus={self.id_virus})>"

def calculer_checksum_fichier(filepath):
    import hashlib

    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        config.log_error(f"Fichier non trouvé: {filepath}")
        return None

def verifier_migration_necessaire(session, filepath):

    filename = os.path.basename(filepath)
    checksum_actuel = calculer_checksum_fichier(filepath)

    if not checksum_actuel:
        return False, "Fichier non trouvé"

    # Vérifier s'il y a une migration existante
    migration_existante = session.query(MigrationStatus).filter(
        MigrationStatus.filename == filename
    ).first()

    if not migration_existante:
        config.log_info(f"Aucune migration précédente trouvée pour {filename}")
        return True, "Première migration"

    if migration_existante.checksum == checksum_actuel:
        config.log_info(f"Fichier {filename} inchangé depuis la dernière migration")
        return False, "Fichier inchangé"

    config.log_info(f"Fichier {filename} modifié depuis la dernière migration")
    return True, "Fichier modifié"

def enregistrer_migration(session, filepath, status="completed"):

    filename = os.path.basename(filepath)
    checksum = calculer_checksum_fichier(filepath)

    if not checksum:
        return

    # Supprimer l'ancienne entrée si elle existe
    session.query(MigrationStatus).filter(
        MigrationStatus.filename == filename
    ).delete()

    # Créer une nouvelle entrée
    nouvelle_migration = MigrationStatus(
        filename=filename,
        checksum=checksum,
        status=status
    )

    session.add(nouvelle_migration)
    session.commit()
    config.log_info(f"Migration enregistrée: {filename} - {status}")

def forcer_migration():
    return os.getenv('FORCE_MIGRATION', 'false').lower() in ['true', '1', 'yes']

def migrer_donnees():
    session = None
    try:
        # Validation du fichier CSV
        config.log_info("Validation du fichier CSV...")
        validator.valider_fichier_csv(config.csv_file_path)

        # Connexion à la base de données
        config.log_info("Connexion à la base de données...")
        engine = create_engine(
            config.get_database_url(),
            echo=False,  # Évite les logs de requêtes
            pool_pre_ping=True,  # Vérification de la connexion
            pool_recycle=3600,   # Recyclage des connexions
        )

        # Création des tables si elles n'existent pas
        config.log_info("Création des tables...")
        Base.metadata.create_all(engine)

        config.log_info("Tables créées/vérifiées avec succès")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Vérifier si la migration est nécessaire
        migration_forcee = forcer_migration()
        if migration_forcee:
            config.log_info("Migration forcée demandée via FORCE_MIGRATION=true")
            migration_necessaire = True
            raison = "Migration forcée"
        else:
            migration_necessaire, raison = verifier_migration_necessaire(session, config.csv_file_path)

        # Marquer la migration comme en cours
        enregistrer_migration(session, config.csv_file_path, "in_progress")

        config.log_info(f"Début de la migration: {raison}")
        config.log_info("Chargement du fichier CSV...")

        try:
            df = pd.read_csv(config.csv_file_path)
            config.log_info(f"Fichier chargé: {len(df)} lignes")
        except Exception as e:
            config.log_error("Erreur lors du chargement du CSV", e)
            enregistrer_migration(session, config.csv_file_path, "failed")
            raise

        config.log_info("Insertion des données de référence...")

        # Insertion des saisons
        saisons_dict = inserer_saisons(session, df)

        # Insertion des pays
        pays_dict = inserer_pays(session, df)

        # Insertion des virus
        virus_dict = inserer_virus(session, df)

        # Insertion des données pour les statistiques journalières
        config.log_info("Insertion des statistiques journalières...")
        inserer_statistiques(session, df, pays_dict, virus_dict, saisons_dict)

        # Insertion des données pour les statistiques globales
        config.log_info("Calcul des statistiques globales...")
        calculer_statistiques_globales(session, df, virus_dict)

        verifier_migration_finale(session)

        # Marquer la migration comme terminée
        enregistrer_migration(session, config.csv_file_path, "completed")

        config.log_info("Migration terminée avec succès - passage en mode veille")
    except Exception as e:
        config.log_error("Erreur critique durant la migration", e)
        if session:
            session.rollback()
            enregistrer_migration(session, config.csv_file_path, "failed")
            config.log_info("Rollback effectué")

        config.log_error(f"Détails de l'erreur: {type(e).__name__}")
        raise
    finally:
        if session:
            session.close()
            config.log_info("Session fermée")

def inserer_saisons(session, df):
    config.log_info("Traitement des saisons...")

    if 'season' not in df.columns:
        config.log_info("Colonne 'season' non trouvée, création d'une saison par défaut")
        return {'default': 1}

    saisons_uniques = df['season'].unique()
    config.log_info(f"Saisons détectées: {len(saisons_uniques)}")

    saisons_dict = {}

    for nom_saison in saisons_uniques:
        try:
            # Vérifie si existe déjà
            saison_existante = session.query(Saisons).filter(Saisons.nom_saison == nom_saison).first()
            if saison_existante:
                saisons_dict[nom_saison] = saison_existante.id_saison
            else:
                nouvelle_saison = Saisons(nom_saison=nom_saison)
                session.add(nouvelle_saison)
                session.flush()
                saisons_dict[nom_saison] = nouvelle_saison.id_saison
        except Exception as e:
            config.log_error(f"Erreur lors de l'insertion de la saison {nom_saison}", e)
            raise

    session.commit()
    config.log_info(f"Saisons traitées: {len(saisons_dict)}")
    return saisons_dict

def inserer_pays(session, df):
    config.log_info("Traitement des pays...")

    pays_info = df.groupby('country').agg({
        'population': 'first'
    }).reset_index()
    config.log_info(f"Pays détectés: {len(pays_info)}")

    pays_dict = {}

    for _, row in pays_info.iterrows():

        nom_pays = row['country']
        population = row['population']

        try:
            # Vérifie si existe déjà
            pays_existant = session.query(Pays).filter(Pays.nom_pays == nom_pays).first()
            if pays_existant:
                pays_dict[nom_pays] = pays_existant.id_pays
            else:
                nouveau_pays = Pays(nom_pays=nom_pays, population=population)
                session.add(nouveau_pays)
                session.flush()
                pays_dict[nom_pays] = nouveau_pays.id_pays
        except Exception as e:
            config.log_error(f"Erreur lors de l'insertion du pays {nom_pays}", e)
            raise

    session.commit()
    config.log_info(f"Pays traités: {len(pays_dict)}")
    return pays_dict

def inserer_virus(session, df):
    config.log_info("Traitement des virus...")

    virus_uniques = df['virus'].unique()
    config.log_info(f"Virus détectés: {len(virus_uniques)}")

    virus_dict = {}

    for nom_virus in virus_uniques:
        try:
            # Vérifie si existe déjà
            virus_existant = session.query(Virus).filter(Virus.nom_virus == nom_virus).first()
            if virus_existant:
                virus_dict[nom_virus] = virus_existant.id_virus
            else:
                nouveau_virus = Virus(nom_virus=nom_virus)
                session.add(nouveau_virus)
                session.flush()
                virus_dict[nom_virus] = nouveau_virus.id_virus
        except Exception as e:
            config.log_error(f"Erreur lors de l'insertion du virus {nom_virus}", e)
            raise

    session.commit()
    config.log_info(f"Virus traités: {len(virus_dict)}")
    return virus_dict

def inserer_statistiques(session, df, pays_dict, virus_dict, saisons_dict):
    # Groupe pour éviter les doublons
    stats_df = df.groupby(['date', 'country', 'virus', 'season']).agg({
        'total_cases': 'max',
        'total_deaths': 'max',
        'new_cases': 'sum',
        'new_deaths': 'sum',
        'case_growth': 'mean',
        'death_rate': 'mean',
        'infection_rate': 'mean',
        'death_rate_pop': 'mean',
        'infection_rate_vs_global': 'mean',
        'death_rate_pop_vs_global': 'mean'
    }).reset_index()

    # Insertion par lots
    lot_size = 1000
    total_lots = (len(stats_df) + lot_size - 1) // lot_size
    config.log_info(f"Insertion en {total_lots} lots de {lot_size}...")

    for i in range(0, len(stats_df), lot_size):
        lot = stats_df.iloc[i:i+lot_size]
        stats_list = []

        for _, row in lot.iterrows():
            try:
                # Résolution des IDs
                id_pays = pays_dict.get(row['country'])
                id_virus = virus_dict.get(row['virus'])

                if not id_pays or not id_virus:
                    config.log_error(f"ID manquant - Pays: {row['country']}, Virus: {row['virus']}")
                    continue

                # Conversion de la date
                try:
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                except ValueError as e:
                    config.log_error(f"Date invalide: {row['date']}", e)
                    continue

                # Résolution de la saison
                id_saison = None
                if 'season' in row and pd.notna(row['season']) and row['season'] in saisons_dict:
                    id_saison = saisons_dict[row['season']]

                # Vérifie si la statistique existe déjà
                stat_existante = session.query(StatistiquesJournalieres).filter(
                    StatistiquesJournalieres.id_pays == id_pays,
                    StatistiquesJournalieres.id_virus == id_virus,
                    StatistiquesJournalieres.date == date_obj
                ).first()

                if not stat_existante:
                    nouvelle_stat = StatistiquesJournalieres(
                        id_pays=id_pays,
                        id_virus=id_virus,
                        id_saison=id_saison,
                        date=date_obj,
                        total_cas=safe_int(row.get('total_cases', 0)),
                        total_deces=safe_int(row.get('total_deaths', 0)),
                        nouveaux_cas=safe_int(row.get('new_cases', 0)),
                        nouveaux_deces=safe_int(row.get('new_deaths', 0)),
                        croissance_cas=safe_float(row.get('case_growth')),
                        taux_mortalite=safe_float(row.get('death_rate')),
                        taux_infection=safe_float(row.get('infection_rate')),
                        taux_mortalite_population=safe_float(row.get('death_rate_pop')),
                        taux_infection_vs_global=safe_float(row.get('infection_rate_vs_global')),
                        taux_mortalite_pop_vs_global=safe_float(row.get('death_rate_pop_vs_global'))
                    )
                    stats_list.append(nouvelle_stat)

            except Exception as e:
                config.log_error(f"Erreur lors du traitement d'une ligne de statistique", e)
                continue

        # Insertion du lot
        if stats_list:
            try:
                session.bulk_save_objects(stats_list)
                session.commit()
                config.log_info(f"Lot {(i // lot_size) + 1}/{total_lots} traité - {len(stats_list)} statistiques")
            except Exception as e:
                config.log_error(f"Erreur lors de l'insertion du lot {(i // lot_size) + 1}", e)
                session.rollback()
                raise

def calculer_statistiques_globales(session, df, virus_dict):
    try:
        global_stats = df.groupby(['date', 'virus']).agg({
            'total_cases': 'sum',
            'total_deaths': 'sum',
            'infection_rate': 'mean',
            'death_rate_pop': 'mean'
        }).reset_index()

        for _, row in global_stats.iterrows():
            try:
                id_virus = virus_dict.get(row['virus'])
                if not id_virus:
                    config.log_error(f"Virus non trouvé pour les stats globales: {row['virus']}")
                    continue

                try:
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                except ValueError as e:
                    config.log_error(f"Date invalide pour stats globales: {row['date']}", e)
                    continue

                # Vérifie si la statistique globale existe déjà
                global_existante = session.query(StatistiquesGlobales).filter(
                    StatistiquesGlobales.id_virus == id_virus,
                    StatistiquesGlobales.date == date_obj
                ).first()

                if not global_existante:
                    nouvelle_global = StatistiquesGlobales(
                        id_virus=id_virus,
                        date=date_obj,
                        total_cas_mondial=safe_int(row.get('total_cases')),
                        total_deces_mondial=safe_int(row.get('total_deaths')),
                        taux_infection_global_moyen=safe_float(row.get('infection_rate')),
                        taux_mortalite_pop_global_moyen=safe_float(row.get('death_rate_pop'))
                    )
                    session.add(nouvelle_global)

            except Exception as e:
                config.log_error(f"Erreur lors du calcul d'une stat globale", e)
                continue

        session.commit()

    except Exception as e:
        config.log_error("Erreur lors du calcul des statistiques globales", e)
        raise

def verifier_migration_finale(session):
    config.log_info("Vérification finale de la migration...")

    try:
        count_pays = session.query(Pays).count()
        count_virus = session.query(Virus).count()
        count_saisons = session.query(Saisons).count()
        count_stats = session.query(StatistiquesJournalieres).count()
        count_global = session.query(StatistiquesGlobales).count()
        count_users = session.query(User).count()

        config.log_info(f"=== RÉSUMÉ DE LA MIGRATION ===")
        config.log_info(f"Pays: {count_pays}")
        config.log_info(f"Virus: {count_virus}")
        config.log_info(f"Saisons: {count_saisons}")
        config.log_info(f"Statistiques journalières: {count_stats}")
        config.log_info(f"Statistiques globales: {count_global}")
        config.log_info(f"Utilisateurs: {count_users}")

        # Vérifications de cohérence
        if count_stats == 0:
            config.log_event("Aucune statistique journalière insérée")
            raise ValueError("Migration incomplète: aucune donnée insérée")

        if count_pays == 0 or count_virus == 0:
            config.log_event("Données de référence manquantes")
            raise ValueError("Migration incomplète: données de référence manquantes")

        config.log_info("Vérification finale réussie")

    except Exception as e:
        config.log_error("Erreur lors de la vérification finale", e)
        raise

def safe_float(value):
    if pd.isna(value) or value == '' or value is None:
        return 0.0
    try:
        result = float(value)
        return result
    except (ValueError, TypeError):
        config.log_event(f"Conversion float impossible: {value}")
        return 0.0

def safe_int(value):
    if pd.isna(value) or value == '' or value is None:
        return 0
    try:
        result = int(float(value))
        return result
    except (ValueError, TypeError):
        config.log_event(f"Conversion int impossible: {value}")
        return 0

if __name__ == "__main__":
    config.log_info("Démarrage du script de migration sécurisé")
    migrer_donnees()
    config.log_info("Migration terminée avec succès")