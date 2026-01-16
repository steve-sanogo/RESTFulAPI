# 🌍 World Data RESTful API

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb&logoColor=white)

## 📝 Description
Ce projet consiste en la réalisation d'une **API RESTful** connectée à un cluster **MongoDB Atlas**. L'objectif est de fournir, modifier et analyser des données démographiques et géographiques sur les pays du monde (population, superficie, capitale, indice Gini, etc.).

Une particularité de cette API est sa gestion sécurisée des modifications : les mises à jour et ajouts ne sont pas appliqués directement à la base principale mais stockés dans une collection temporaire (`update`) pour validation par un administrateur.

Ce projet a été réalisé dans le cadre du module **Base de données NoSQL** (INGC2 - Année 2021/2022).

## 🗄️ Architecture de la Base de Données
Le projet utilise **MongoDB Atlas** avec une base de données nommée `world` contenant deux collections principales :

1.  **`countries`** : Contient les données réelles des pays (nom, capitale, population, région, etc.).
2.  **`update`** : Stocke les demandes de modifications ou d'ajouts. Chaque document inclut des métadonnées comme `modificationDate`, `modificationHour` et un statut `processed` (False par défaut).

## 🚀 Installation et Configuration

### Prérequis
* Python 3.x
* Compte MongoDB Atlas (avec un Cluster configuré)

### Installation des dépendances
Installez les bibliothèques nécessaires (Flask, PyMongo, DNSPython) :

```bash
pip install flask
python -m pip install pymongo
python -m pip install dnspython
```

### Configuration

Assurez-vous de configurer votre chaîne de connexion MongoDB Atlas dans le fichier principal (`main.py`) :

```python
cluster = MongoClient("mongodb+srv://<username>:<password>@cluster0.kafpl.mongodb.net/...")
```

## 🔌 Endpoints de l'API

### 🔍 Consultation (GET)

L'API offre de nombreuses possibilités d'agrégation et de recherche :

| Méthode | Route | Description |
| --- | --- | --- |
| `GET` | `/countries/count` | Retourne le nombre total de pays. |
| `GET` | `/country/<region>/<name>` | Infos sur un pays spécifique (ex: `/country/Africa/Burkina Faso`). |
| `GET` | `/country/<region>/<name>/<field>` | Retourne un champ précis d'un pays (ex: ses frontières). |
| `GET` | `/countries/<region>/<field>` | Liste une info pour tous les pays d'un continent. |
| `GET` | `/countries/<region>/<subregion>/<field>` | Liste une info pour tous les pays d'une sous-région (ex: `Western Africa`). |
| `GET` | `/continent/<region>/<subregion>/<op>/<field>` | **Agrégation** (Somme/Moyenne) sur une sous-région. |
| `GET` | `/continent/<region>/<op>/<field>` | **Agrégation** (Somme/Moyenne) sur un continent entier. |
| `GET` | `/world/<op>/<field>` | **Agrégation** mondiale (ex: `/world/average/area`). |

> **Note :** `<op>` (opération) peut être `count` ou `average`.

### ✏️ Modification et Ajout (PUT & POST)

Toutes les modifications sont enregistrées dans la collection `update`.

| Méthode | Route | Description |
| --- | --- | --- |
| `PUT` | `/country/update/<field>` | Demande de mise à jour d'un seul champ. |
| `PUT` | `/country/update/<field1>/<field2>` | Demande de mise à jour de deux champs simultanément. |
| `PUT` | `/country/update/all` | Demande de mise à jour complète (name, capital, population, area, gini). |
| `POST` | `/add/country` | Demande d'ajout d'un nouveau pays. |

## 🛠 Technologies Utilisées

* **Langage :** Python
* **Framework Web :** Flask (Micro-framework)
* **SGBD :** MongoDB (Atlas Cloud)
* **Driver :** PyMongo