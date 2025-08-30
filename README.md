# ANALYZE-IT

Ce projet est une plateforme d'analyse et de prédiction de pandémie multi-pays (France, Suisse, USA).

## Prérequis

- Node.js >= 18
- Python >= 3.10
- Docker & Docker Compose

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/ANALYZE-IT.git
cd ANALYZE-IT
```

### 2. Configurer les variables d'environnement

Copiez le fichier `.env.example` en `.env` dans le dossier racine et adaptez les variables d’environnement selon le pays et les ports souhaités.

### 3. Lancer les bases de données et services avec Docker Compose

```bash
# Pour la France
docker compose -f docker-compose.fr.yml up -d

# Pour la Suisse
docker compose -f docker-compose.ch.yml up -d

# Pour les USA
docker compose -f docker-compose.usa.yml up -d
```

Accédez à l’application sur l’URL et le port définis dans votre fichier `.env` (par exemple : `http://localhost:<PORT>`).

---

# Livrables

- Des scripts et configurations pour le déploiement de l'infrastructure : voir https://github.com/TheLordGibril/ansible-analyze-it
- Des fichiers Docker pour la conteneurisation des solutions. : Dockerfile dans frontend/, ml_api/ et backend/, et 3 fichiers Docker Compose à la racine du projet, un par pays.
- Des mécanismes de sauvegarde et de restauration des données et des services. : Dans le projet Ansible : roles/docker/files/backup, il y a un fichier `entrypoint.sh` qui est exécuté au lancement du docker compose de prod, et si on veut restorer, le script `restore.sh` restaure la dernière sauvegarde qui a été effectuée.
- Des fichiers relatifs aux pipelines d'intégration et des déploiements continus, incluant les étapes de build, test, analyse de code, et déploiement. : .github/worflows/main.yml

- Une documentation détaillée du pipeline, avec des instructions pour son utilisation et sa maintenance. : Voir PDF
- Une documentation détaillée de vos images Docker/ Podman : Voir PDF
- Des rapports de tests automatisés et indicateurs de qualité de code. : Générés dans les annotations de Github Actions, par exemple : https://github.com/TheLordGibril/ANALYZE-IT/actions/runs/17325212828 en bas de page.
- Une documentation de l'architecture système en format UML. : Voir PDF

- Des rapports de sprint incluant les objectifs et les réalisations. : Voir PDF
- Un tableau Kanban illustrant l’avancement des tâches. : Voir PDF
- La présentation de l’ensemble des cérémonies utilisées en fonction du choix de votre méthode agile. : Voir PDF