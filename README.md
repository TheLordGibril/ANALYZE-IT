# 📦 Livrables - Projet d’analyse de données pandémiques

## 1. Modèle de données UML

- UML : `csv_to_postgres/schema BDD.svg`
- MCD : `csv_to_postgres/MCD.svg`
- MLD : `csv_to_postgres/MLD.svg`
- MPD : `csv_to_postgres/MPD.svg`

Représentation complète du schéma relationnel de la base de données utilisée pour centraliser les différentes sources de données.

---

## 2. Base de données relationnelle & script de création

Afin de créer la base de données PostgreSQL, veuillez télécharger la suite logicielle PostgreSQL :

👉 [PostgreSQL - EnterpriseDB](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)

### Étapes de mise en place :

1. Installer PostgreSQL et pgAdmin.
2. Lancer pgAdmin et créer un **nouveau serveur**.
    - Exemple :
        - Nom du serveur : `localhost`
        - Hostname : `localhost`
        - Username : `postgres` ou celui défini à l'installation de PostgreSQL
        - Mot de passe : celui défini à l’installation de PostgreSQL
3. Créer une **nouvelle base de données** nommée `MSPR`.

---

## 3. Mise en fonctionnement de l’Apollo Server

**GraphQL** permet des requêtes souples et ciblées sur les données nettoyées.

### Configuration des variables d’environnement

Avant de lancer le serveur, configurez les variables d’environnement nécessaires à la connexion à la base de données PostgreSQL.

1. Copiez le fichier `.env.example` en `.env` dans le dossier `backend` :

```bash
cp .env.example .env
```

2. Ouvrez le fichier `.env` et remplacez les valeurs par défaut par vos informations réelles, notamment le **mot de passe** et le **nom d’utilisateur** PostgreSQL si vous les avez modifiés lors de l’installation.

Exemple de section à modifier dans `.env` :

```
DATABASE_URL="postgresql://<utilisateur>:<mot_de_passe>@localhost:5432/MSPR?schema=public"
```

Assurez-vous que ces informations correspondent à celles de votre instance PostgreSQL.

### Installation des dépendances

Depuis le dossier `backend` :

```bash
npm install
```

### Déploiement des migrations Prisma

```bash
npx prisma migrate deploy
```

### Génération du client Prisma

```bash
npx prisma generate
```

### Lancement du serveur

```bash
npm run start
```

---

## 4. Importation des données dans la base

Depuis le dossier `csv_to_postgres` :

1. Créer un environnement virtuel :

```bash
py -m venv venv
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Lancer le script d’importation :

```bash
py migration-script.py
```

---

## 5. Code ETL

📁 Notebook Jupyter : `etl/data_cleaning.ipynb`

Contient l’ensemble du processus de préparation, nettoyage et fusion des données brutes.

---

## 6. Documentation API (OpenAPI Spec)

Le fichier `backend/openapi.yaml` est ouvrable avec l'outil suivant, fourni par Swagger : https://swagger.io/tools/swagger-editor/

---

## 7. Tableau de bord interactif

**Outil utilisé :** Power BI

**Objectif :**

Observer l’évolution de la contamination et de la mortalité des virus COVID-19 et de la variole du singe dans le monde.

### Sources de données

- Base de données PostgreSQL
- Tables : `Pays`, `Virus`, `Statistiques journalières`

### Indicateurs clés

**Statistiques journalières :**

- **Contamination** : Nombre total de cas, nombre de nouveaux cas, taux d’infection → *deuxième page*
- **Mortalité** : Nombre total de décès, nombre de nouveaux décès, taux de mortalité → *troisième page*

### Fonctionnalités

- Sélection des pays → *Première page*
- Sélection du virus → *Première page*
- Parcours des périodes (années, trimestres, mois, jours) → *via interaction avec les graphiques*

### Justification

Nous avons souhaité que l’utilisation de Power BI soit la plus simple possible pour l’utilisateur, notamment grâce à un design agréable et épuré.

Afin d’améliorer la lisibilité des graphiques, la section "Filtres" a été séparée sur une première page dédiée.

Il est possible d’y sélectionner un virus à l’aide de boutons radio, car la visualisation simultanée des données des deux virus n’est pas lisible.

Pour la sélection des pays, plusieurs options sont possibles : ne rien sélectionner, tout sélectionner (pour avoir les données mondiales), ou choisir un pays ou un groupe de pays grâce à la barre de recherche.

### Visualisation des données

Chaque page affiche 6 éléments d’information :

1. Le nom de la page actuelle (en gras)
2. Le virus sélectionné
3. Le(s) pays sélectionné(s) :
    - Si aucun ou tous les pays sont sélectionnés → **Monde entier**
    - Si un seul pays est sélectionné → **Nom du pays**
    - Si plusieurs pays sont sélectionnés → **"Plusieurs pays sélectionnés"**
4. Un graphique de l’évolution des cas totaux dans le temps
5. Un graphique de l’évolution des nouveaux cas dans le temps
6. Un graphique de l’évolution des taux (de mortalité ou de contamination) dans le temps

### Choix des visualisations

- **Cas totaux** : affichés sous forme de courbe pour faciliter la lecture dans le temps, notamment avec un grand volume de données journalières.
- **Nouveaux cas et taux** : affichés sous forme de graphiques en barres, permettant :
    - La comparaison visuelle avec les périodes précédentes
    - L’exploration de plages temporelles précises (grâce à l’interaction avec les barres)
    - La descente dans la hiérarchie temporelle (année → trimestre → mois → jour) via le mode exploration
    - La possibilité de remonter dans la hiérarchie à l’aide du bouton situé à gauche du graphique

---

## 8. Documentation détaillée : collecte et nettoyage des données

> La fusion des jeux de données repose sur une normalisation préalable de chaque source pour garantir une homogénéité avant la fusion. Cela permet de minimiser les incohérences et de limiter le nettoyage post-fusion.

### Étapes clés :

1. Suppression des colonnes inutiles et harmonisation des noms
2. Gestion des valeurs manquantes (suppression ou imputation)
3. Formatage des types (dates, float, etc.)
4. Vérification de la cohérence intercolonnes
5. Suppression des doublons intradataset
6. Fusion des datasets
7. Détection de doublons interdatasets après fusion
8. Feature Engineering :
    - Taux de croissance des cas
    - Taux de mortalité
    - % de population touchée
    - Saisonnalité
    - Moyennes mondiales de référence

Vous trouverez plus de détails dans le fichier `etl/data_cleaning.ipynb` concernant la démarche suivie. Le code est commenté et documenté.

---

## 9. Benchmark des solutions techniques

### **ETL & Préparation**

- `Pandas` → Référence en traitement CSV
- `Jupyter Notebook` → Itération rapide et visualisation instantanée

---

### **Stockage des données**

- **PostgreSQL (choix)** → Choix principal, robuste & intégré
- **Alternatives** :
    - MySQL / MariaDB → Bonne alternative si PostgreSQL n’est pas requis
    - DuckDB → Idéal pour requêtes analytiques sur des fichiers locaux
    - ClickHouse → Très rapide pour de la data analytique
    - BigQuery → Si besoin de requêter des datasets massifs sur le cloud
- **ORMs** :
    - Prisma (Node.js) → ORM typé, moderne et multi-SGBD
    - SQLAlchemy (Python) → Intégré pour l’export depuis le notebook

---

### **API & CRUD**

- **GraphQL (choix)** → Requêtage ciblé et structuré comme demandé
- **REST (FastAPI, Express.js)** → Standard mais moins souple
- **Librairies** : Apollo Server (Node.js)

---

### **Visualisation des données**

- **Power BI (choix)** → Recommandé pour filtres, export, et dashboards clairs
- **Matplotlib**, **Seaborn** → Explorations initiales
- **Plotly**, **Bokeh** → Graphiques interactifs
- **Apache Superset**, **Metabase** → Solutions open-source

---

## 10. Diagramme de Gantt

`Gantt.png`