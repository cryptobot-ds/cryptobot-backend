# 🐳 CryptoBot — Docker (Build & Run)

Cette documentation décrit comment CryptoBot est **conteneurisé** et exécuté sur une instance **EC2** via **Docker Compose**.

Deux modes sont disponibles :
- **Développement / local** : `docker-compose.yml` (build depuis le code)
- **Production (EC2)** : `docker-compose.prod.yml` (images pré-build sur Docker Hub)

---

## 🧱 Services (conteneurs)

| Service           | Container name            | Rôle                                   | Port(s)                   |
| ----------------- | ------------------------- | -------------------------------------- | ------------------------- |
| **API**           | `cryptobot_api`           | API FastAPI (backend)                  | `8000`                    |
| **Dashboard**     | `cryptobot_dashboard`     | Interface utilisateur Streamlit        | `8501`                    |
| **MLflow**        | `cryptobot_mlflow`        | UI de suivi des expériences ML         | `5000`                    |
| **Prometheus**    | `cryptobot_prometheus`    | Collecte des métriques système/app     | `9090`                    |
| **Grafana**       | `cryptobot_grafana`       | Visualisation des dashboards           | `3000`                    |
| **Node Exporter** | `cryptobot_node_exporter` | Métriques de l’hôte + fichiers `.prom` | *(scrapé par Prometheus)* |
| **cAdvisor**      | `cryptobot_cadvisor`      | Métriques des conteneurs Docker        | `8080` *(interne)*        |


Réseau Docker :
- `cryptobot_net` (réseau dédié aux services)

Volumes persistants :
- `prometheus_data` : stockage Prometheus
- `grafana_data` : stockage Grafana
- `/home/ubuntu/mlflow_data/mlruns:/mlruns` : persistance des runs MLflow sur l’EC2

---

## 📁 Organisation des fichiers

À la racine du projet :
- `docker-compose.yml` : mode build (dev/local)
- `docker-compose.prod.yml` : mode prod (EC2)
- `monitoring/prometheus.yml` : configuration Prometheus

---

## ⚙️ Configuration (.env)

Tous les services applicatifs utilisent un fichier d’environnement externe sur l’EC2 :

- `/home/ubuntu/cryptobot_env/.env`

Il contient notamment les variables de connexion PostgreSQL (RDS) et les paramètres applicatifs nécessaires.

---

## ▶️ Lancer en production (EC2)

Depuis la racine du projet :

```bash
docker compose -f docker-compose.prod.yml up -d
```
Vérifier :
```
docker ps
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

Arrêter :
```
docker compose -f docker-compose.prod.yml down
```

🧪 Lancer en local / dev (build depuis le code)
```
docker compose up -d --build
```

🔒 Ressources limitées (prod)

Le fichier docker-compose.prod.yml définit des limites CPU/RAM (exemples) :

- API : cpus: 0.50, mem_limit: 350m

- Dashboard : cpus: 0.50, mem_limit: 350m

- Prometheus / Grafana / MLflow : limites adaptées à l’EC2

Objectif : éviter qu’un service monopolise les ressources et garantir la stabilité globale.

### 🧠 MLflow (UI + stockage local)

MLflow est lancé dans un conteneur python:3.12-slim et installe MLflow au démarrage :

Backend store : file:/mlruns

Stockage persistant EC2 : /home/ubuntu/mlflow_data/mlruns

Accès UI :

http://<EC2_PUBLIC_IP>:5000

>Note : l’usage d’un backend filesystem est suffisant pour un projet pédagogique. Une amélioration future serait d’utiliser un backend base de données (SQLite/PostgreSQL).

### 📊 Monitoring (Prometheus / Grafana)

Prometheus scrape :

- prometheus:9090

- node-exporter:9100

- cadvisor:8080

### Grafana :

http://<EC2_PUBLIC_IP>:3000

Identifiants définis via variables d’environnement (admin / password)

Les métriques CRON custom (ETL/ML) sont exposées via Node Exporter (textfile collector) :
```
/var/lib/node_exporter/textfile_collector/cryptobot_cron.prom
```

### ✅ Endpoints utiles (EC2)

API : http://<EC2_PUBLIC_IP>:8000

Dashboard : http://<EC2_PUBLIC_IP>:8501

MLflow : http://<EC2_PUBLIC_IP>:5000

Prometheus : http://<EC2_PUBLIC_IP>:9090

Grafana : http://<EC2_PUBLIC_IP>:3000

###  Dépannage rapide
Port déjà utilisé
```
sudo lsof -i :5000
docker ps
```
Voir les logs d’un service
```
docker logs -f cryptobot_api
docker logs -f cryptobot_prometheus
docker logs -f cryptobot_mlflow
```

Rebuild complet (dev)
```
docker compose down
docker compose up -d --build
```