# 📈 CryptoBot – Module Machine Learning

Ce module constitue la partie **Machine Learning** du projet `cryptobot-backend`. Il permet la **prédiction des prix** de trois cryptomonnaies : **Bitcoin**, **Ethereum** et **BNB**, avec insertion automatique des résultats dans une base de données PostgreSQL.

---

##  Table des matières

- [Structure du projet](#structure-du-projet)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Docker](#docker)
- [Modèle ML](#modèle-ml)
- [Logs](#logs)
- [Évolutions prévues](#évolutions-prévues)
- [License](#license)

---

## 🗂️ Structure du projet

ml/
├── init.py # Rend le dossier importable comme package Python
├── predict_price.py # Script principal de prédiction et insertion BDD
├── train_model.py # (À venir) Entraînement et sauvegarde du modèle
├── features_engineering.py # (À venir) Préparation et sélection des features
├── Dockerfile # Dockerfile spécifique au module ML


Les prédictions sont stockées dans la table `predictions` de la base de données PostgreSQL (RDS).

---

##  Fonctionnalités

- Récupération de l'historique depuis la table `crypto_prices`
- Nettoyage et sélection intelligente des features
- Construction de la cible : `price(t+1)`
- Pipeline ML scikit-learn avec :
  - `SimpleImputer`, `StandardScaler`, `Ridge`
  - Validation croisée `TimeSeriesSplit` (MAE)
  - Évaluation avec `MAE` et `Directional Accuracy`
- Prédiction du prochain prix + décision (`BUY` / `SELL` / `HOLD`)
- Insertion en base avec `ON CONFLICT DO NOTHING`

---

## ⚙️ Installation

### En local

```bash
# Depuis la racine du projet
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
 Configuration

Le script supporte deux modes :

En local (fichier .env à la racine) :
```bash
DB_HOST=...
DB_NAME=cryptobot
DB_USER=cryptobot_user
DB_PASSWORD=...
DB_PORT=5432
```
Sur serveur (fichier ~/.cryptobot_env) :
```bash
DB_HOST=...
DB_NAME=cryptobot
DB_USER=cryptobot_user
DB_PASSWORD=...
DB_PORT=5432
```
Le module charge d'abord .env, puis surcharge avec ~/.cryptobot_env s'il est présent.
 Utilisation
En local
```bash
source .venv/bin/activate
python -m ml.predict_price
```

Sur serveur (EC2)
```bash
cd ~/actions-runner/_work/cryptobot-backend/cryptobot-backend
source .venv/bin/activate
python -m ml.predict_price
```
---
🐳 Docker
```bash
Dockerfile (ml/Dockerfile)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "ml.predict_price"]
```
Exécution
```bash
docker run --env-file .env cryptobot-ml
```
---
🧠 Modèle ML
- Pipeline scikit-learn

- Imputation : SimpleImputer(strategy="median")

- Standardisation : StandardScaler()

- Régression : Ridge(alpha=1.0)

- Validation

- Validation croisée : TimeSeriesSplit(n_splits=5)

- Métrique principale : Mean Absolute Error (MAE)

- Directional Accuracy : précision directionnelle (hausse/baisse)

- Prise de décision

- Basée sur la variation entre predicted_price et last_price

- Résultats : BUY, SELL, HOLD
---
## 📄 Logs

Les logs sont enregistrés dans :

- logs/ml_predict.log
---

##  Évolutions prévues

 - Implémentation de train_model.py

- Entraînement sur l'historique complet

- Sauvegarde du modèle (ml/model.pkl)

-  Factorisation des features dans features_engineering.py

 - Intégration de MLflow :

- Suivi des versions, métriques, hyperparamètre