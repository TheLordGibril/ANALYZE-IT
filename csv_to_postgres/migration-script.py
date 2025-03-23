import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
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
    
    statistiques = relationship("StatistiquesJournalieres", back_populates="pays")
    
    def __repr__(self):
        return f"<Pays(id_pays={self.id_pays}, nom_pays={self.nom_pays})>"

class Virus(Base):
    __tablename__ = "Virus"
    
    id_virus = Column(Integer, primary_key=True, autoincrement=True)
    nom_virus = Column(String(50), unique=True, nullable=False)
    
    statistiques = relationship("StatistiquesJournalieres", back_populates="virus")
    
    def __repr__(self):
        return f"<Virus(id_virus={self.id_virus}, nom_virus={self.nom_virus})>"

class StatistiquesJournalieres(Base):
    __tablename__ = "Statistiques_Journalieres"
    
    id_stat = Column(Integer, primary_key=True, autoincrement=True)
    id_pays = Column(Integer, ForeignKey("Pays.id_pays"), nullable=False)
    id_virus = Column(Integer, ForeignKey("Virus.id_virus"), nullable=False)
    date = Column(Date, nullable=False)
    nouveaux_cas = Column(Integer, default=0, nullable=False)
    nouveaux_deces = Column(Integer, default=0, nullable=False)
    total_cas = Column(Integer, default=0, nullable=False)
    total_deces = Column(Integer, default=0, nullable=False)
    
    # Relations
    pays = relationship("Pays", back_populates="statistiques")
    virus = relationship("Virus", back_populates="statistiques")
    
    # Contrainte d'unicité composée
    __table_args__ = (
        UniqueConstraint('id_pays', 'id_virus', 'date', name='Statistiques_Journalieres_id_pays_id_virus_date_key'),
    )
    
    def __repr__(self):
        return f"<StatistiquesJournalieres(id_stat={self.id_stat}, date={self.date}, pays={self.id_pays}, virus={self.id_virus})>"

def migrer_donnees():
    try:
        # Connexion à la base de données
        print("Connexion à la base de données...")
        engine = create_engine(DATABASE_URL)
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
        stats_df = df.groupby(['date', 'country', 'virus']).agg({
            'new_cases': 'sum',
            'new_deaths': 'sum',
            'computed_total_cases': 'max',
            'computed_total_deaths': 'max'
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
                            nouveaux_cas=int(row['new_cases']) if not np.isnan(row['new_cases']) else 0,
                            nouveaux_deces=int(row['new_deaths']) if not np.isnan(row['new_deaths']) else 0,
                            total_cas=int(row['computed_total_cases']) if not np.isnan(row['computed_total_cases']) else 0,
                            total_deces=int(row['computed_total_deaths']) if not np.isnan(row['computed_total_deaths']) else 0
                        )
                        stats_list.append(nouvelle_stat)
                except Exception as e:
                    print(f"Erreur lors du traitement de la ligne: {row}")
                    print(str(e))
            
            if stats_list:
                session.bulk_save_objects(stats_list)
                session.commit()
            
            print(f"Lot {(i // lot_size) + 1}/{total_lots} traité")
        
        # Vérification finale
        count_pays = session.query(Pays).count()
        count_virus = session.query(Virus).count()
        count_stats = session.query(StatistiquesJournalieres).count()
        
        print(f"Migration terminée. Résumé:")
        print(f"- Pays: {count_pays}")
        print(f"- Virus: {count_virus}")
        print(f"- Statistiques journalières: {count_stats}")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Démarrage de la migration des données...")
    migrer_donnees()
    print("Migration terminée.")
