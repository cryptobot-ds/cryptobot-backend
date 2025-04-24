# cryptobot-backend

## Getting started - Unix (MacOS/Linux)

### Installation de PostgreSQL et création du `.venv`

**S'assurer que PostgreSQL est installé sur la machine :**

- MacOS avec [Homebrew](https://brew.sh/) : `brew install postgresql@17 && brew services start postgresql@17`
- Sur Ubuntu et dérivés : `sudo apt update && sudo apt install -y postgresql postgresql-contrib libpq-dev`
   
**Installer les dépendances :**

Script shell qui supprime le `.venv` et le recréé en installant les dépendances à partir du `requirements.txt` :

```shell
chmod +x setup_venv.sh
./setup_venv.sh
```

Si erreur avec `pg_config` sur Mac :

```shell
# S'assurer que pg_config est bien présent :
brew list postgresql@17 | grep pg_config

# L'ajouter au $PATH :
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
source ~/.zshrc
```

## Création de la base de données en local

### Initialisation

1. Vérifier la version de PostgreSQL :

```shell
psql --version
```
2. Se connecter à PostgreSQL avec l’utilisateur postgres :

```shell
psql -U postgres

# Sur Mac
createdb # because Macs don't create username databases after installing PostgreSQL
psql
```

3. Créer un utilisateur et une base de données :

```postgres
CREATE USER cryptobot_user WITH PASSWORD 'securepassword';
CREATE DATABASE cryptobot_db OWNER cryptobot_user;
GRANT ALL PRIVILEGES ON DATABASE cryptobot_db TO cryptobot_user;
\q
```

### Création de la base de données

1. Se connecter à la base de données avec l’utilisateur créé :

```shell
psql -U cryptobot_user -d cryptobot_db -W
# mdp
```

2. Création de la table :

```postgres
CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    crypto TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    price DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION,
    rsi DOUBLE PRECISION,
    macd DOUBLE PRECISION,
    macd_signal DOUBLE PRECISION,
    macd_histogram DOUBLE PRECISION,
    sma DOUBLE PRECISION,
    upper_band DOUBLE PRECISION,
    lower_band DOUBLE PRECISION,
    adx DOUBLE PRECISION,
    stoch_rsi DOUBLE PRECISION,
    fibo_23 DOUBLE PRECISION,
    fibo_38 DOUBLE PRECISION,
    fibo_50 DOUBLE PRECISION,
    fibo_61 DOUBLE PRECISION,
    fibo_78 DOUBLE PRECISION,
    volume_avg_7d DOUBLE PRECISION,
    volume_avg_14d DOUBLE PRECISION,
    volume_avg_30d DOUBLE PRECISION,
    sma_7 DOUBLE PRECISION,
    sma_14 DOUBLE PRECISION,
    sma_30 DOUBLE PRECISION,
    fear_greed_7d DOUBLE PRECISION,
    fear_greed_14d DOUBLE PRECISION,
    fear_greed_30d DOUBLE PRECISION,
    change_percent DOUBLE PRECISION,
    UNIQUE (crypto, timestamp)
);
```

Pour se déconnecter de la base de données :

```postgres
\q
```

## Import de données antérieures dans la base

1. Connexion :

```shell
psql -U cryptobot_user -d cryptobot_db -W
```

2. Copie des données

```postgres
\copy crypto_prices FROM '/chemin/vers/export_crypto_prices.csv' DELIMITER ';' CSV HEADER;

-- ou si l'export contient moins de colonnes que l'actuel schema de db

\copy crypto_prices(id, crypto, timestamp, price, volume, rsi, macd, sma, macd_signal, macd_histogram, upper_band, lower_band, adx, stoch_rsi, fibo_23, fibo_38, fibo_50, fibo_61, fibo_78)
FROM 'export_crypto_prices.csv' DELIMITER ';' CSV HEADER;
```

## Lancement des scripts

Créer un fichier `.env` qui sera importé par `bot.py` sous le format :

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost # car local
DB_PORT=5432 # port par défaut en local
```