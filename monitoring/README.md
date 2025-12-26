# 📊 CryptoBot — Monitoring (Prometheus + Grafana)

Cette brique fournit l’**observabilité** de CryptoBot :
- supervision de l’hôte (EC2) via **Node Exporter**
- supervision des conteneurs Docker via **cAdvisor**
- supervision du pipeline (ETL/ML) via des **métriques custom CRON** (textfile collector)
- visualisation dans **Grafana**

Objectif : détecter rapidement un incident (CRON KO, ressources saturées) et démontrer que le système tourne réellement “en production”.

---

## 🧱 Stack & conteneurs

Conteneurs Docker en production :

- `cryptobot_prometheus` (Prometheus) — port **9090**
- `cryptobot_grafana` (Grafana) — port **3000**
- `cryptobot_node_exporter` (Node Exporter) — port **9100**
- `cryptobot_cadvisor` (cAdvisor) — port **8080**
- `cryptobot_mlflow` (MLflow UI) — port **5000**
- `cryptobot_api` (FastAPI) — port **8000**
- `cryptobot_dashboard` (Streamlit) — port **8501**

> Remarque : l’API n’expose pas encore `/metrics` (optionnel, amélioration future).

---

## 📁 Emplacement des fichiers

À la racine du projet :
- `docker-compose.yml` / `docker-compose.prod.yml`
- dossier `monitoring/`

Dans `monitoring/` :
- `monitoring/prometheus.yml` : configuration Prometheus
- `monitoring/README.md` : cette documentation

---

## ⚙️ Configuration Prometheus

Fichier : `monitoring/prometheus.yml`

Jobs scrappés :
- `prometheus` → `prometheus:9090`
- `node-exporter` → `node-exporter:9100`
- `cadvisor` → `cadvisor:8080`

---

## ⏱️ Monitoring du pipeline CRON (métriques custom)

Le pipeline ETL/ML tourne automatiquement via **cron** (EC2) et publie un statut de santé via Prometheus.

### Textfile collector (Node Exporter)

Node Exporter est configuré avec le **textfile collector** :

- Dossier hôte : `/var/lib/node_exporter/textfile_collector`
- Fichier écrit : `cryptobot_cron.prom`

Le script `collect_data/collect_data.sh` écrit à chaque run :

- `cryptobot_cron_last_success_timestamp` : timestamp UNIX du dernier succès
- `cryptobot_cron_last_failure_timestamp` : timestamp UNIX du dernier échec
- `cryptobot_cron_last_run_status` : 1 (OK) / 0 (KO)

➡️ En cas d’erreur, un `trap` publie automatiquement un statut KO.

---

## 📈 Dashboards Grafana

Dashboards principaux :

### 1) Containers (cAdvisor)
- **CPU usage (containers)**
- **Memory usage (containers)**

### 2) Pipeline CRON
- **Dernier CRON réussi** (stat basé sur `cryptobot_cron_last_success_timestamp`)
- **CRON status** (OK/KO via `cryptobot_cron_last_run_status`)

> Les dashboards peuvent être exportés/importés via Grafana (JSON).  
> L’essentiel côté README est de décrire les métriques et comment les vérifier.

---

## ✅ Vérifications rapides

### 1) Vérifier que les targets Prometheus sont UP
Aller sur :
- `http://<EC2_PUBLIC_IP>:9090/targets`

Attendu :
- `prometheus` = UP
- `node-exporter` = UP
- `cadvisor` = UP

### 2) Vérifier le fichier CRON exporté
Sur l’EC2 :
```bash
cat /var/lib/node_exporter/textfile_collector/cryptobot_cron.prom
```

## 📊 3) Vérification dans Prometheus / Grafana

Une fois les métriques exposées via le **Node Exporter textfile collector**, tu peux les interroger dans **Prometheus Explore** ou les visualiser dans **Grafana**.

---

### 🧠Requêtes système utiles (Docker / Node Exporter)

#### 🔄 CPU par conteneur (via cAdvisor)
```
sum by (id) (
  rate(container_cpu_usage_seconds_total{
    job="cadvisor",
    id=~"/system\\.slice/docker-.*\\.scope"
  }[2m])
) * 100
```
Affiche l’utilisation CPU par conteneur Docker (peut dépasser 100% si multi-cœurs).

 RAM par conteneur Docker (MB)
```
container_memory_working_set_bytes{job="cadvisor"} / 1024 / 1024
```
 Espace disque disponible (%) — partition /

```
(node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100
```
Mémoire machine (Node Exporter)
Totale : node_memory_MemTotal_bytes

Disponible : node_memory_MemAvailable_bytes

📌 Notes
Les métriques cryptobot_cron_... sont générées par collect_data.sh via un fichier .prom.

status == 1 ✅ (OK)

status == 0 ❌ (échec)

>Des seuils visuels (vert / orange / rouge) sont configurés dans Grafana afin d’identifier rapidement une saturation >CPU ou mémoire.

--- 

### 🔐 Notes sécurité

Les métriques ne contiennent aucune donnée personnelle.

Les secrets (BDD, etc.) restent externalisés via variables d’environnement.

Les dashboards servent à la supervision du projet et à la démonstration (cadre pédagogique).

--- 

### ✅ Améliorations futures (optionnel)

Ajouter un endpoint /metrics à l’API FastAPI pour suivre :

latence, erreurs HTTP, nombre de requêtes

Mettre en place une alerte Grafana :

CRON status = 0 (KO) sur une fenêtre de X minutes

