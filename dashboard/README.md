# 📊 CryptoBot — Dashboard (Streamlit)

Cette brique fournit une **interface de visualisation** pour CryptoBot.
Elle permet :
- de consulter la **dernière prédiction ML** (prix actuel, prix prédit, MAE, décision BUY/SELL/HOLD)
- de visualiser le **sentiment marché** via le **Fear & Greed Index**
- d’explorer les **indicateurs techniques** calculés (RSI, MACD, Bollinger, ADX, Stoch RSI, etc.)
- le tout en lisant directement les données stockées dans **PostgreSQL (AWS RDS)**

---

## 🧱 Fichiers principaux

- `dashboard/dashboard.py` : application Streamlit principale
- (Docker) le dossier `dashboard/` contient le build de l’image dashboard

---

## 🔌 Source des données (PostgreSQL / RDS)

Le dashboard interroge deux tables :

### 1) `predictions`
Utilisée pour afficher la dernière prédiction ML (par crypto) :
- `last_price`
- `predicted_price`
- `decision` (BUY / SELL / HOLD)
- `model_mae`
- `timestamp`

Requête utilisée (simplifiée) :
- dernière ligne pour une crypto, triée par timestamp DESC

### 2) `crypto_prices`
Utilisée pour afficher les courbes prix + indicateurs :
- `timestamp`, `price`
- `rsi`, `macd`, `macd_signal`, `macd_histogram`
- `sma`, `upper_band`, `lower_band`
- `adx`, `stoch_rsi`
- niveaux Fibonacci (`fibo_23`, `fibo_38`, `fibo_50`, `fibo_61`, `fibo_78`)

### 3) `fear_greed_index`
Utilisée pour afficher la jauge de sentiment (dernière valeur) :
- `value`
- `classification` (Fear / Greed…)

---

## ⚙️ Configuration (.env)

Le dashboard utilise les variables suivantes :

```env
DB_HOST=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_PORT=5432
```
En production (EC2), ces variables sont fournies via :
```
/home/ubuntu/cryptobot_env/.env
```
▶️ Lancer en local (dev)

Pré-requis : Python + accès DB
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Lancer Streamlit :
```
streamlit run dashboard/dashboard.py
```

Accès :
```
http://localhost:8501
```
### 🐳 Lancer avec Docker Compose

En production (EC2), le dashboard est exposé en 8501:8501.
```
docker compose -f docker-compose.prod.yml up -d
docker ps
```

Accès :
```
http://<EC2_PUBLIC_IP>:8501
```
### 🖥️ Fonctionnement de l’UI

L’interface utilisateur permet de visualiser les données, consulter les prédictions ML et explorer les indicateurs techniques pour chaque cryptomonnaie sélectionnée.

---

### 🔎 Sélection de la cryptomonnaie

L’utilisateur peut choisir parmi les cryptos suivantes :

- 🟠 **Bitcoin** (`bitcoin`)
- 🟣 **Ethereum** (`ethereum`)
- 🟡 **Binance Coin** (`binancecoin`)

---

### 📈 Bloc "Prédiction du prix pour demain"

Ce bloc affiche :

- 🔮 La dernière prédiction disponible depuis la table `predictions`
- 🟩🟥🟨 Un encart coloré selon la décision du modèle :

- | 🟢 **BUY**  | Vert |
- | 🔴 **SELL** | Rouge |
- | 🟡 **HOLD** | Jaune |

---

### 😨 Fear & Greed Index

- 📊 Jauge interactive Plotly allant de `0` (peur extrême) à `100` (avidité extrême)
- 🏷️ Affichage de la classification actuelle :
  - *Extreme Fear*, *Fear*, *Neutral*, *Greed*, *Extreme Greed*

---

### 📊 Graphiques techniques (Plotly)

Pour chaque crypto sélectionnée, l’UI affiche plusieurs visualisations :

- 📈 **Prix** (historique)
- 📉 **RSI** (*Relative Strength Index*)  
  ➤ Seuils visuels : `70` (sur-achat) / `30` (sur-vente)
- 📉 **MACD**  
  ➤ Ligne MACD, signal et histogramme
- 📊 **Bandes de Bollinger**  
  ➤ Moyenne mobile + bandes supérieure/inférieure
- 📉 **ADX** (*Average Directional Index*)  
  ➤ Seuil de tendance : `25`
- 📉 **Stochastic RSI**  
  ➤ Seuils : `80` (sur-achat) / `20` (sur-vente)

---


✅ Dépannage rapide
“Pas de prédiction disponible”

Ca veut dire que la table predictions est vide (ou pas alimentée récemment).

Solution :

- lancer le module ML (sur EC2 : via le CRON / ETL, ou manuellement)

- vérifier que le pipeline écrit bien en base

- Erreur de connexion DB

- vérifier les variables .env

- vérifier l’accessibilité réseau RDS (security group / whitelist)

- vérifier les credentials