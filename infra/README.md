# 🏗️ CryptoBot — Infrastructure (AWS / EC2 / RDS)

Cette section décrit l’infrastructure Cloud utilisée pour héberger le projet **CryptoBot**.
L’objectif est de fournir une architecture :
- simple,
- fiable,
- économique,
- adaptée à un projet Data / ML en production légère.

---

## ☁️ Vue d’ensemble

L’infrastructure repose sur **AWS** et comprend :

- une instance **EC2** (Linux) pour :
  - l’exécution des pipelines ETL & ML (cron)
  - l’hébergement des conteneurs Docker (API, Dashboard, Monitoring, MLflow)
- une base de données **PostgreSQL sur RDS** pour :
  - le stockage des données crypto
  - les features
  - les prédictions ML

---

## 🧱 Composants principaux

### 1) Instance EC2

- Fournisseur : AWS
- Type : EC2 Linux (Ubuntu)
- Rôle :
  - serveur applicatif
  - orchestrateur Docker
  - exécution des scripts Python (ETL / ML)
  - supervision (Prometheus / Grafana)

Fonctions hébergées sur l’EC2 :
- API FastAPI
- Dashboard Streamlit
- MLflow UI
- Prometheus
- Grafana
- Node Exporter
- cAdvisor
- CRON système (pipeline horaire)

---

### 2) Base de données — PostgreSQL (RDS)

- Service : AWS RDS
- Moteur : PostgreSQL
- Accès :
  - uniquement depuis l’EC2 (réseau privé / security group)
- Rôle :
  - stockage des données historiques (`crypto_prices`)
  - stockage du sentiment (`fear_greed_index`)
  - stockage des prédictions ML (`predictions`)

La base est **externe aux conteneurs**, ce qui garantit :
- persistance des données
- découplage infra / applicatif
- simplicité de sauvegarde

---

## 🌐 Réseau & sécurité

### Security Groups

- **EC2**
  - ports ouverts :
    - 22 (SSH – accès administrateur)
    - 8000 (API)
    - 8501 (Dashboard)
    - 3000 (Grafana)
    - 9090 (Prometheus)
    - 5000 (MLflow)
  - accès public limité au strict nécessaire

- **RDS**
  - port : 5432
  - accès restreint :
    - uniquement depuis le Security Group de l’EC2

---

## 🔐 Gestion des secrets

Les secrets ne sont **jamais commités** dans le dépôt Git.

Ils sont fournis via :
- un fichier `.env`
- ou `/home/ubuntu/cryptobot_env/.env` sur l’EC2

Exemples de variables :
```env
DB_HOST=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_PORT=5432
``` 
## ⚙️ Variables & secrets

Ces variables sont injectées :

- dans les conteneurs Docker (`env_file`)
- dans les scripts Python exécutés par `cron`

---

## 🐳 Conteneurisation (Docker)

L’ensemble des services applicatifs est conteneurisé :

- **API FastAPI**
- **Dashboard Streamlit**
- **MLflow**
- **Prometheus**
- **Grafana**
- **Node Exporter**
- **cAdvisor**

Deux environnements sont définis :

- `docker-compose.yml` → **Développement**
- `docker-compose.prod.yml` → **Production**

### 🚀 En production :

- Images **pré‑buildées** : `bricesensei/cryptobot-*`
- **Limites CPU / RAM** définies
- **Redémarrage automatique** : `restart: unless-stopped`

---

## ⏱️ Orchestration & automatisation

### 🕒 CRON (ETL / ML)

Un cron système est configuré sur l’EC2 :

- **Fréquence** : toutes les heures
- **Script exécuté** : `collect_data/collect_data.sh`

Ce script orchestre :

1. la collecte des données
2. le calcul des indicateurs techniques
3. le feature engineering
4. l’insertion en base
5. la prédiction ML
6. l’exposition des métriques Prometheus

---

## 📊 Monitoring & observabilité

L’infrastructure est supervisée via :

| `Node Exporter` | Métriques système EC2 |

| `cAdvisor` | Métriques des conteneurs Docker |

| `Prometheus` | Collecte des métriques |

| `Grafana` | Visualisation des dashboards |

Des métriques custom sont exposées pour :

- le **statut du pipeline CRON**
- la **date du dernier succès / échec**

---

## 📈 Schéma logique (texte)

- [ Cron EC2 ]
↓
- [ ETL / ML scripts ]
↓
- [ PostgreSQL RDS ]
↓
- [ API / Dashboard ]
↓
- [ Utilisateur ]

---

## 🎯 Choix d’architecture (justification)

- **EC2 unique** : simplicité + coût maîtrisé
- **RDS managé** : persistance, backups, fiabilité
- **Docker** : isolation, reproductibilité
- **Batch CRON** : adapté à un pipeline data non temps réel
- **Monitoring** : preuve de fonctionnement réel (Prometheus/Grafana)

---

## 🔄 Évolutions possibles

- séparation API / ETL sur plusieurs instances
- autoscaling
- ajout d’un endpoint `/metrics` sur l’API
- orchestration avancée via **Airflow** ou **Step Functions**
- pipeline distribué multi‑instances

---

## 🏗️ Provisionnement de l’infrastructure (Terraform– IaC)

L’infrastructure AWS de CryptoBot a été **provisionnée via Terraform** dans une approche *Infrastructure as Code (IaC)*.

“IaC” coche plusieurs cases d’un coup :
- reproductibilité
- versionnement
- industrialisation
- séparation infra / applicatif


L'IaC (Terraform) permet de :
- décrire l’infrastructure de manière déclarative,
- versionner la configuration,
- reproduire l’environnement de façon fiable,
- limiter les erreurs manuelles.

Les ressources gérées incluent notamment :
- l’instance **EC2** (compute),
- la base **RDS PostgreSQL**,
- les **Security Groups**,
- les règles réseau associées.

👉 Terraform est utilisé **pour créer et maintenir l’infrastructure**,  
mais **n’intervient pas dans l’exécution applicative quotidienne** (ETL, ML, API).

Cette séparation garantit :
- une infrastructure stable,
- une exploitation applicative indépendante.

---
---

## ⚙️ Configuration serveur (Ansible)

Une fois l’infrastructure provisionnée, la configuration logicielle de l’instance EC2
est automatisée à l’aide de **Ansible**.

Ansible est utilisé pour :
- l’installation des dépendances système,
- la préparation de l’environnement Linux,
- l’installation de Docker et Docker Compose,
- la configuration des services nécessaires au projet.

Cette approche permet :
- un serveur reproductible,
- une configuration documentée,
- une réduction des opérations manuelles.

👉 Ansible intervient **au niveau système** (OS / services),
tandis que Docker gère l’exécution des applications.

---
