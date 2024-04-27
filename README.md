# Orange du Projet

## Description

Ce projet est une API construite avec FastAPI pour gérer des notifications et des messages utilisateurs via Firebase et stocker les données dans MongoDB. Elle permet d'enregistrer des tokens d'utilisateurs, d'envoyer des notifications et de visualiser les messages envoyés.

## Technologies Utilisées

- FastAPI : Un framework moderne, rapide (haute performance), pour construire des API avec Python 3.7+ basé sur des standards Python type hints.
- Firebase : Plateforme développée par Google pour la création d'applications mobiles et web.
- MongoDB : Base de données NoSQL qui offre une grande flexibilité et des performances élevées pour les applications modernes.

## Fonctionnalités

- Enregistrement et mise à jour des tokens d'utilisateurs.
- Envoi de notifications via Firebase.
- Insertion et consultation des messages envoyés stockés dans MongoDB.

## Configuration du Projet

### Prérequis

Vous aurez besoin de Python 3.7+ installé sur votre machine, ainsi que de `pip` pour gérer les paquets Python. Assurez-vous aussi d'avoir accès à une instance MongoDB et à un projet Firebase.

### Installation des Dépendances

Clonez ce dépôt et installez les dépendances nécessaires en exécutant :

```bash
pip install fastapi uvicorn firebase-admin pymongo jinja2
