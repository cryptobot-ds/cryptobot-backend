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
## 🧠 Modèle ML explication
### Justification des choix ML
Le modèle retenu est une régression linéaire régularisée (Ridge).
Ce choix est volontairement simple et frugal, afin de garantir :

- une bonne interprétabilité des résultats,

- une stabilité face à la volatilité des données,

- un coût de calcul réduit, compatible avec une exécution batch régulière.

- La validation repose sur un split temporel (TimeSeriesSplit), afin de respecter la nature séquentielle des données financières et d’éviter toute fuite d’information entre le passé et le futur.

Les métriques utilisées sont :

- `MAE (Mean Absolute Error)` pour mesurer la précision des prédictions de prix,

- `Directional Accuracy` pour évaluer la capacité du modèle à prédire correctement la direction du marché (hausse / baisse), critère essentiel pour la prise de décision.

### Pipeline Machine Learning

Pipeline scikit-learn :

- Imputation : `SimpleImputer(strategy="median")`

- Standardisation : `StandardScaler()`

- Régression : `Ridge(alpha=1.0)`

Validation :

- Validation croisée temporelle : `TimeSeriesSplit(n_splits=5)`
- Métrique principale : `Mean Absolute Error (MAE)`

- Métrique secondaire : `Directional Accuracy`

- Stratégie de décision `(BUY / SELL / HOLD)`

- La décision est basée sur la comparaison entre :

- le prix prédit `(predicted_price)`

- le dernier prix observé `(last_price)`

Une zone de neutralité (seuil) est appliquée afin d’éviter les décisions basées sur des variations marginales liées au bruit du marché.

###  Règles de Décision

La décision est basée sur la **variation relative** entre le prix prédit par le modèle
(`predicted_price`) et le dernier prix observé (`last_price`).

- 🟢 **BUY (Vert)** :  
  Le signal d’achat est généré lorsque la variation relative dépasse un **seuil positif**.

- 🔴 **SELL (Rouge)** :  
  Le signal de vente est déclenché lorsque la variation relative passe sous un **seuil négatif**.

- ⚪️ **HOLD (Neutre)** :  
  Si la variation relative reste comprise entre les deux seuils, aucune action n’est déclenchée.


---
### Éthique et frugalité

Ce module respecte une approche éthique et frugale :

- aucune exécution de trading réel,

- aucune donnée personnelle collectée ou traitée,

- utilisation de données publiques uniquement,

- modèle volontairement simple (pas de deep learning),

- exécution batch horaire via cron, limitant la consommation de ressources.

- Cette approche garantit une solution responsable, maîtrisée et adaptée à un contexte de projet Data Engineer.

### Stockage des résultats

- Chaque exécution du module :

- calcule une prédiction et une décision,

- insère les résultats dans la table predictions de la base PostgreSQL (RDS),

- permet la consultation via l’API FastAPI et le dashboard Streamlit.
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

## 📄 Logs

Les logs sont enregistrés dans :

- logs/ml_predict.log
---

## 🔍 MLflow – Tracking & versioning

MLflow est utilisé pour assurer le suivi et la traçabilité des exécutions du modèle.

À chaque exécution du script `predict_price.py`, les éléments suivants sont enregistrés :

- paramètres du modèle (type de modèle, hyperparamètres),
- métriques d’évaluation (MAE, Directional Accuracy),
- artefacts (liste des features utilisées),
- modèle entraîné.

Les runs MLflow sont exécutés automatiquement toutes les heures (via cron)
pour chaque cryptomonnaie (BTC, ETH, BNB) et persistés sur l’instance EC2
à l’aide d’un backend de type filesystem :

`/home/ubuntu/mlflow_data/mlruns`

Cette approche garantit la **reproductibilité**, le **versioning des modèles**
et le **suivi des performances dans le temps**, sans complexité excessive.

---

##  Évolutions prévues

 - Implémentation de train_model.py

- Entraînement sur l'historique complet

- Sauvegarde du modèle (ml/model.pkl)

-  Factorisation des features dans features_engineering.py

- Amélioration du suivi MLflow :
  - comparaison de plusieurs modèles,
  - enrichissement des métriques suivies,
  - historisation avancée des performances.
