## 1) 📥 EXTRACT — Sources de données

Sources utilisées (données publiques uniquement) :

- CoinGecko : prix/historique (api.coingecko.com)

- Binance : prix spot temps réel (api.binance.com)

- Fear & Greed Index : sentiment crypto (api.alternative.me)

Les cryptomonnaies suivies :

- Bitcoin (bitcoin / BTC)

- Ethereum (ethereum / ETH)

- Binance Coin (binancecoin / BNB)

---

## 2) 🧪 TRANSFORM — Indicateurs & features calculées
Indicateurs techniques (calculés dans bot.py)

Exemples :

- RSI

- SMA

- MACD (signal + histogram)

- Bandes de Bollinger (upper/lower)

- (selon implémentation : ADX, Stoch RSI, Fibonacci...)

- Feature engineering (dans generate_features.py)

- Ajouts principaux (upsert en base) :

- volume_avg_7d, volume_avg_14d, volume_avg_30d

- sma_7, sma_14, sma_30

- fear_greed_7d, fear_greed_14d, fear_greed_30d

- change_percent (variation %)

Objectif : produire des variables stables et exploitables pour le ML et l’analyse.

---

## 3) 🗃️ LOAD — Stockage PostgreSQL (RDS)

Les données sont chargées dans PostgreSQL (AWS RDS) :

- Table crypto_prices

- prix, volume + indicateurs + features

- upsert via : ON CONFLICT (crypto, timestamp) DO UPDATE

- Table fear_greed_index

- index de sentiment (horodaté)

Ce mécanisme garantit :

- pas de doublons

- mise à jour des features si recalculées

- un stockage “propre” et cohérent pour le ML/API

---
> ℹ️ **Séparation ETL / ML**  
> Le module Machine Learning consomme les données produites par l’ETL,
> mais ne fait pas partie du pipeline ETL au sens strict.
>  
> L’ETL a pour objectif de produire des données fiables et exploitables,
> tandis que le ML constitue une étape aval dédiée à la prédiction et à l’analyse.

---

### ⏱️ Automatisation (cron)

Le pipeline est conçu pour être exécuté automatiquement :

- Cron (toutes les heures) → appelle collect_data/collect_data.sh

Le script orchestre :

- collecte / calculs / insertion

- génération de features

- archivage / nettoyage

- (optionnel) check BDD

- (optionnel) lancement du ML (ml/predict_price.py)

---

### 🧹 Archivage & rétention

Le script archive_and_clean.py :

archive les fichiers (CSV / logs) dans */archives/

supprime automatiquement les fichiers trop anciens (rétention configurée, ex : 30 jours)

Objectifs :

- limiter l’encombrement disque

- conserver une traçabilité minimale

- rester frugal en stockage

---

### 📈 Monitoring (Node Exporter textfile collector)

Le script collect_data.sh écrit un fichier de métriques Prometheus :

dossier : /var/lib/node_exporter/textfile_collector

fichier : cryptobot_cron.prom

Exemples de métriques :

- timestamp du dernier succès

- statut du dernier run (OK / KO)

Cela permet d’intégrer la santé du pipeline dans Grafana/Prometheus.

---

### 🔐 Sécurité & conformité

Données publiques uniquement (pas de données personnelles)

Secrets externalisés via variables d’environnement (.env / ~/.cryptobot_env)

Accès BDD via compte dédié (RDS)

Pipeline batch (pas de service critique exposé)

---

### Frugalité (coût maîtrisé)

Exécution horaire en batch (pas de streaming continu)

Modèle simple et calculs limités

Archivage + rétention pour limiter le stockage

Réutilisation des données en base (pas de re-collecte inutile)

---

### ▶️ Exécution manuelle (debug)
Pré-requis
```
python -m venv .venv
source .venv/bin/activate
pip install -r collect_data/requirements.txt
```
Lancer 
```
cd collect_data
bash collect_data.sh
```

Lancer uniquement les features
python generate_features.py

###  🔎 Sorties attendues

- Nouvelles lignes / mises à jour dans crypto_prices et fear_greed_index

- CSV mis à jour dans csv/

- logs (si activés)

- métriques .prom mises à jour 


---

## 🧩 Orchestration (collect_data.sh)

Le script `collect_data.sh` orchestre l’exécution complète du pipeline :
En cas d’échec à n’importe quelle étape, le script s’arrête immédiatement (set -e) et publie un statut KO via Prometheus.

1. Chargement des variables d’environnement depuis `~/.cryptobot_env`
2. Activation (ou création) d’un environnement virtuel Python `.venv`
3. Installation des dépendances : `pip install -r requirements.txt`
4. Exécution :
   - `bot.py` : collecte + calcul indicateurs + insertion BDD
   - `archive_and_clean.py` : archivage + rétention CSV/logs
   - `generate_features.py` : feature engineering + upsert
   - `../bdd/check_db.py` (si présent) : vérification basique
   - `../ml/predict_price.py` : prédiction + insertion + tracking MLflow
5. Publication métriques Node Exporter :
   - succès → `cryptobot_cron_last_success_timestamp` + status=1
   - échec → `cryptobot_cron_last_failure_timestamp` + status=0


## 🧭 Flow (résumé)

Cron (toutes les heures)  
→ `collect_data/collect_data.sh` (orchestrateur)  
→ `bot.py` + `archive_and_clean.py` + `generate_features.py` + `ml/predict_price.py`  
→ PostgreSQL (RDS) + CSV + logs + métriques Prometheus


---

## ⏱️ Planification (cron)

Le pipeline est planifié avec `cron` sur l’EC2 :

```cron
10 * * * * /home/ubuntu/actions-runner/_work/cryptobot-backend/cryptobot-backend/collect_data/collect_data.sh >> /home/ubuntu/actions-runner/_work/cryptobot-backend/cryptobot-backend/logs/collect_data_cron.log 2>&1
```

Exécution : toutes les heures à HH:10

`Logs : logs/collect_data_cron.log`


## 📈 Monitoring (Node Exporter textfile collector)

À la fin de chaque exécution, le script écrit un fichier de métriques Prometheus :

- Dossier : `/var/lib/node_exporter/textfile_collector`
- Fichier : `cryptobot_cron.prom`

Métriques exposées :
- `cryptobot_cron_last_success_timestamp` : timestamp UNIX du dernier succès
- `cryptobot_cron_last_failure_timestamp` : timestamp UNIX du dernier échec
- `cryptobot_cron_last_run_status` : 1 (OK) / 0 (KO)

En cas d’erreur à n’importe quelle étape, un `trap` déclenche l’écriture des métriques en échec.


## 🔁 Consommation (ML / API / Dashboard)

Les données stockées en base (RDS) alimentent :
- le module ML (`ml/predict_price.py`) exécuté dans la même orchestration cron,
- l’API FastAPI (consultation des prédictions / historique),
- le dashboard Streamlit (visualisation).
