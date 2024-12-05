# Projet de Fin d'Année : Prédiction de la Catégorie d'un Film

Ce projet consiste à développer une application Flask capable de prédire la catégorie d'un film (`bien`, `moyen` ou `médiocre`) en fonction de plusieurs caractéristiques :  
- **Revenus**  
- **Budget**  
- **Nombre de votes sur TMDB**  
- **Durée du film**  

L'objectif est d'utiliser un modèle d'intelligence artificielle entraîné sur des données réelles pour fournir des prédictions directement à travers une interface web.

---

## **Fonctionnalités**
- **Prédictions en temps réel** grâce à une interface web développée avec Flask.  
- **API REST** exposée via FastAPI pour interagir avec le modèle d'IA et la base de données.  
- **Entraînement et benchmarking** de modèles pour trouver les algorithmes les plus performants.  
- **Monitorage** des métriques de performance et des ressources grâce à Prometheus et Grafana.  

---

## **Technologies et Outils Utilisés**
- **Flask** : Framework web pour la création de l'interface utilisateur.  
- **FastAPI** : Pour exposer une API REST.  
- **MLFLOW** : Suivi des expérimentations et gestion des modèles via Dagshub.  
- **MySQL** : Stockage des données.  
- **Prometheus & Grafana** : Monitorage et visualisation des performances.  
- **Docker-Compose** : Pour lancer l'application et ses services dans un environnement conteneurisé.  

---

## **Structure du Projet**
Le projet est organisé en plusieurs dossiers :  

### `api/`  
Ce dossier contient tout ce qui concerne l'API développée avec FastAPI. On y trouve le code permettant d'exposer le modèle d'IA sous forme d'API REST ainsi que les différentes requêtes SQL vers la base de données.  

### `donnees/`  
Tout ce qui touche à la collecte et la préparation des données pour entraîner le modèle. Cela inclut les scripts pour récolter les données ainsi qu'effectuer des nettoyages et sauvegarder les données dans une base MySQL.  

### `entrainement/`  
On y trouve ici tout le processus d'entraînement et de benchmarking des modèles. Ce dossier contient les scripts pour tester différents algorithmes et hyperparamètres à l'aide de MLFLOW.  

### `prometheus_data/`  
Ce dossier contient le fichier `prometheus.yml` pour la configuration de Prometheus. Il est utilisé pour monitorer les performances de l'application et les métriques du modèle.  

### `web/`  
Le code source de l'application Flask se trouve ici. Ce dossier contient les fichiers nécessaires à la création de l'interface utilisateur qui permet d'interagir avec le modèle.  

---

## **Lancer l'Application**
L'ensemble du projet utilise Docker-Compose pour simplifier le lancement et la gestion des différents services.  
