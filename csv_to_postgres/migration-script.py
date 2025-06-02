import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData, Column, Integer, BigInteger, Numeric, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


# Configuration de la connexion à la base de données
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/MSPR"

# Définition des modèles SQLAlchemy
Base = declarative_base()

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

def migrer_donnees():
    try:
        # Connexion à la base de données
        print("Connexion à la base de données...")
        engine = create_engine(DATABASE_URL)
        
        # Création des tables si elles n'existent pas
        print("Création des tables...")
        Base.metadata.create_all(engine)
        
        print("Tables créées/vérifiées avec succès")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Vérification si les tables existent déjà (pas besoin de les créer)
        print("Vérification des tables...")
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Chargement du fichier CSV
        print("Chargement du fichier CSV...")
        df = pd.read_csv('../etl/datasets/final_dataset.csv')
        total_lignes = len(df)
        print(f"Nombre total de lignes dans le CSV: {total_lignes}")
        
        # Extraction des saisons uniques
        saison_uniques = df['season'].unique()
        print(f"Nombre de saison uniques: {len(saison_uniques)}")
        
        # Initialisation des saisons de référence
        print("Initialisation des saisons...")
        saisons_dict = {}
        
        for nom_saison in saison_uniques:
            saison_existante = session.query(Saisons).filter(Saisons.nom_saison == nom_saison).first()
            if saison_existante:
                saisons_dict[nom_saison] = saison_existante.id_saison
            else:
                nouvelle_saison = Saisons(nom_saison=nom_saison)
                session.add(nouvelle_saison)
                session.flush()
                saisons_dict[nom_saison] = nouvelle_saison.id_saison
        
        session.commit()
        print("Saisons initialisées avec succès")
        
        
        # Extraction des pays uniques
        pays_uniques = df['country'].unique()
        print(f"Nombre de pays uniques: {len(pays_uniques)}")
        
        # Insertion des pays
        print("Insertion des pays...")
        pays_dict = {}  # Pour stocker les mappings nom_pays -> id_pays
        
        for nom_pays in pays_uniques:
            # Vérifier si le pays existe déjà
            pays_existant = session.query(Pays).filter(Pays.nom_pays == nom_pays).first()
            if pays_existant:
                pays_dict[nom_pays] = pays_existant.id_pays
            else:
                nouveau_pays = Pays(nom_pays=nom_pays)
                session.add(nouveau_pays)
                session.flush()  # Pour obtenir l'ID généré
                pays_dict[nom_pays] = nouveau_pays.id_pays
        
        session.commit()
        print("Pays insérés avec succès")
        
        # Extraction des virus uniques
        virus_uniques = df['virus'].unique()
        print(f"Nombre de virus uniques: {len(virus_uniques)}")
        
        # Insertion des virus
        print("Insertion des virus...")
        virus_dict = {}  # Pour stocker les mappings nom_virus -> id_virus
        
        for nom_virus in virus_uniques:
            # Vérifier si le virus existe déjà
            virus_existant = session.query(Virus).filter(Virus.nom_virus == nom_virus).first()
            if virus_existant:
                virus_dict[nom_virus] = virus_existant.id_virus
            else:
                nouveau_virus = Virus(nom_virus=nom_virus)
                session.add(nouveau_virus)
                session.flush()  # Pour obtenir l'ID généré
                virus_dict[nom_virus] = nouveau_virus.id_virus
        
        session.commit()
        print("Virus insérés avec succès")
        
        # Préparation des données pour les statistiques journalières
        print("Préparation des statistiques journalières...")
        
        # Grouper par pays, virus, date pour éviter les doublons
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
        
        # Insertion des statistiques journalières par lots car trop de data
        lot_size = 1000
        total_lots = (len(stats_df) + lot_size - 1) // lot_size
        print(f"Insertion des statistiques en {total_lots} lots de {lot_size}...")
        
        for i in range(0, len(stats_df), lot_size):
            lot = stats_df.iloc[i:i+lot_size]
            stats_list = []
            
            for _, row in lot.iterrows():
                try:
                    id_pays = pays_dict[row['country']]
                    id_virus = virus_dict[row['virus']]
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    
                    id_saison = None
                    if 'season' in row and row['season'] in saisons_dict:
                        id_saison = saisons_dict[row['season']]
                    
                    
                    # Vérifier si cette statistique existe déjà
                    stat_existante = session.query(StatistiquesJournalieres).filter(
                        StatistiquesJournalieres.id_pays == id_pays,
                        StatistiquesJournalieres.id_virus == id_virus,
                        StatistiquesJournalieres.date == date_obj
                    ).first()
                    
                    if not stat_existante:
                        nouvelle_stat = StatistiquesJournalieres(
                            id_pays=id_pays,
                            id_virus=id_virus,
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
                    print(f"Erreur lors du traitement de la ligne: {row}")
                    print(str(e))
            
            if stats_list:
                session.bulk_save_objects(stats_list)
                session.commit()
            
            print(f"Lot {(i // lot_size) + 1}/{total_lots} traité")
        
        global_stats = df.groupby(['date', 'virus']).agg({
            'total_cases': 'sum',
            'total_deaths': 'sum',
            'infection_rate': 'mean',
            'death_rate_pop': 'mean'
        }).reset_index()
        
        for _, row in global_stats.iterrows():
            try:
                id_virus = virus_dict[row['virus']]
                date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                
                # Vérifier si cette statistique globale existe déjà
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
                print(f"Erreur lors du calcul des stats globales: {str(e)}")
        
        session.commit()
        print("Statistiques globales calculées")
        
        # Vérification finale
        count_pays = session.query(Pays).count()
        count_virus = session.query(Virus).count()
        count_saisons = session.query(Saisons).count()
        count_stats = session.query(StatistiquesJournalieres).count()
        count_global = session.query(StatistiquesGlobales).count()

        
        print(f"Migration terminée. Résumé:")
        print(f"- Pays: {count_pays}")
        print(f"- Virus: {count_virus}")
        print(f"- Saisons: {count_saisons}")
        print(f"- Statistiques journalières: {count_stats}")
        print(f"- Statistiques globales: {count_global}")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

def safe_float(value):
    if pd.isna(value) or value == '':
        return 0
    try: 
        return float(value)
    except (ValueError, TypeError):
        return 0
        
def safe_int(value):
    if pd.isna(value) or value == '':
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

if __name__ == "__main__":
    print("Démarrage de la migration des données...")
    migrer_donnees()
    print("Migration terminée.")
