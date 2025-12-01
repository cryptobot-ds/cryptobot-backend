import os
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error

# Charger variables d’environnement

load_dotenv()

# Logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'bot.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Cryptos et features
cryptos = {"bitcoin":"btc", "ethereum":"eth", "binancecoin":"bnb"}
REQUIRED = [
    "price","rsi","macd","macd_signal","macd_histogram","sma",
    "upper_band","lower_band","adx","stoch_rsi","volume",
    "fibo_23","fibo_38","fibo_50","fibo_61","fibo_78",
    "volume_avg_7d","change_percent","sma_7","fear_greed_7d"
]
OPTIONAL = [
    "volume_avg_14d","volume_avg_30d","sma_14","sma_30",
    "fear_greed_14d","fear_greed_30d"
]

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def fetch_data(crypto):
    q = "SELECT * FROM crypto_prices WHERE crypto=%s ORDER BY timestamp ASC"
    with get_connection() as conn:
        return pd.read_sql_query(q, conn, params=(crypto,))

def select_features(df, features, thresh=0.9):
    corr = df[features].corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    drop = [col for col in upper.columns if any(upper[col] > thresh)]
    return [f for f in features if f not in drop]

def decide_action(last, pred, th=0.01):
    d = (pred - last) / last
    return "BUY" if d > th else "SELL" if d < -th else "HOLD"

def predict_price(name, code):
    try:
        df = fetch_data(name)

        # 1) diagnostics avant nettoyage
        raw_n = len(df)
        print(f"🔎 {name} : {raw_n} lignes avant nettoyage")

        feats_all = REQUIRED + [c for c in OPTIONAL if c in df.columns]
        na_counts = df[feats_all].isnull().sum()
        print(f"🔍 NaN par feature pour {name} :")
        print(na_counts[na_counts > 0])

        # 2) on drop les lignes sans features requises
        df = df.dropna(subset=REQUIRED)
        cleaned_n = len(df)
        print(f"🔎 {name} : {cleaned_n} lignes après nettoyage")

        # 3) on construit la liste finale des features et on sélectionne
        feats = REQUIRED + [c for c in OPTIONAL if c in df.columns]
        feats = select_features(df, feats, thresh=0.9)
        logging.info(f"{name} features retenues: {feats}")

        # 4) on prépare target et X/Y
        df["target"] = df["price"].shift(-1)
        df = df.dropna(subset=["target"])
        X = df[feats]
        y = df["target"]

        if len(X) < 10:
            logging.warning(f"{name} trop peu de lignes ({len(X)})")
            return

        # 5) pipeline imputer → scaler → ridge
        pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model",  Ridge(alpha=1.0))
        ])

        # 6) validation temporelle
        tscv = TimeSeriesSplit(n_splits=5)
        scores = -cross_val_score(
            pipe, X, y, cv=tscv,
            scoring="neg_mean_absolute_error"
        )
        logging.info(f"{name} MAE CV: {scores.mean():.2f} ± {scores.std():.2f}")

        # 7) split final, entraînement et test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, shuffle=False, test_size=0.2
        )
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        mae_test = mean_absolute_error(y_test, y_pred)

        # 8) directional accuracy
        sign_true = np.sign(y_test.values - X_test["price"].values)
        sign_pred = np.sign(y_pred - X_test["price"].values)
        dir_acc = (sign_true == sign_pred).mean()

        # 9) prédiction pour la dernière ligne
        last_row = df.iloc[[-1]][feats]
        pred_next = float(pipe.predict(last_row)[0])
        last_price = float(df["price"].iloc[-1])
        decision = decide_action(last_price, pred_next)

        # 10) log & insert
        msg = (
            f"{name.upper()} → Prédiction: {pred_next:.2f} USD, "
            f"MAE_test: {mae_test:.2f}, DirAcc: {dir_acc:.2%}, "
            f"Décision: {decision}"
        )
        print("✅", msg)
        logging.info(msg)
        insert_prediction(name, pred_next, last_price, decision, mae_test)

    except Exception as e:
        logging.error(f"Erreur {name}: {e}")
        print("❌ Erreur:", e)

def insert_prediction(crypto, pred, last, decision, mae, version="v2"):
    ts = datetime.now()
    q = """
    INSERT INTO predictions
      (crypto,timestamp,predicted_price,last_price,decision,model_mae,model_version)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (crypto,timestamp) DO NOTHING;
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(q, (crypto, ts, pred, last, decision, mae, version))
        conn.commit()
        cur.close()
    print(f"✅ {crypto} inséré en BDD")

if __name__ == "__main__":
    # faire un print de l'heure now
    print("Heure actuelle :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for n, c in cryptos.items():
        predict_price(n, c)

