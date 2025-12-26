# 🚀 CryptoBot — CI/CD (GitHub Actions)

CryptoBot utilise **GitHub Actions** pour automatiser :
- des **sanity checks Python** (ETL + feature engineering) exécutés sur l’EC2 (runner self-hosted)
- une **CI Docker** (build + push des images API/Dashboard sur Docker Hub)
- une **CD** (déploiement automatique sur EC2 via Docker Compose)

Les workflows se trouvent dans : `.github/workflows/`.

---

## 🧭 Vue d’ensemble

1) **Push sur `main`**
- Lance `main.yml` : exécution Python sur l’EC2 (ETL + features)
- Lance `ci.yml` : build + push Docker Hub (API + Dashboard)
2) Si la CI Docker réussit :
- Lance `cd.yml` automatiquement : pull + up des conteneurs en production sur EC2

---

## ✅ Workflow 1 — Tests / Sanity checks Python (ETL)

📄 Fichier : `.github/workflows/main.yml`  
🎯 Objectif : valider que le pipeline Data tourne (collecte + features)

**Trigger**
- `push` sur `main`

**Runner**
- `self-hosted` (EC2)

**Étapes**
- Checkout du code (sans nettoyage du workspace)
- Création d’un venv `.venv` + installation des dépendances `requirements.txt`
- Exécution :
  - `collect_data/bot.py` (collecte + calcul indicateurs + insertion BDD)
  - `collect_data/generate_features.py` (feature engineering + upsert)

> Ce workflow joue le rôle de “test d’intégration minimal” (sanity check), et non de tests unitaires.

---

## ✅ Workflow 2 — CI Docker (Build & Push)

📄 Fichier : `.github/workflows/ci.yml`  
🎯 Objectif : builder et publier les images Docker sur Docker Hub

**Trigger**
- `push` sur `main`

**Runner**
- `ubuntu-latest`

**Images publiées**
- `bricesensei/cryptobot-api`
- `bricesensei/cryptobot-dashboard`

**Tags**
- `latest`
- `${{ github.sha }}` (tag versionné par commit)

**Secrets requis**
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

---

## ✅ Workflow 3 — CD (Deploy sur EC2)

📄 Fichier : `.github/workflows/cd.yml`  
🎯 Objectif : déployer automatiquement sur l’EC2 via Docker Compose

**Trigger**
- `workflow_run` : démarre lorsque le workflow CI (`CI - Build & Push Docker images`) est terminé
- Condition : uniquement si `conclusion == success`

**Runner**
- `self-hosted` (EC2)

**Déploiement**
- Login Docker Hub
- Nettoyage disque préventif (prune)
- Déploiement :
  - `docker compose -f docker-compose.prod.yml pull`
  - `docker compose -f docker-compose.prod.yml up -d --remove-orphans`
- Nettoyage post-déploiement (suppression des anciennes images)

---

## 📦 Production (Docker Compose)

Le déploiement utilise : `docker-compose.prod.yml`  
Les services en production incluent notamment :
- API (FastAPI) : `8000`
- Dashboard (Streamlit) : `8501`
- MLflow UI : `5000`
- Monitoring : Prometheus `9090`, Grafana `3000`, Node Exporter `9100`, cAdvisor `8080`

---

## 🧪 Améliorations futures (optionnel)

- Ajouter des **tests unitaires** (pytest) dans la CI (avant build/push)
- Ajouter un endpoint `/metrics` sur l’API pour Prometheus
- Ajouter une étape de **lint** (ruff/black) pour fiabiliser la qualité de code
