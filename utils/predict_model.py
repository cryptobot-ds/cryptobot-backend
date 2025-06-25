import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

REQUIRED_FEATURES = [
    "price", "rsi", "macd", "macd_signal", "macd_histogram", "sma",
    "upper_band", "lower_band", "adx", "stoch_rsi", "volume",
    "fibo_23", "fibo_38", "fibo_50", "fibo_61", "fibo_78",
    "volume_avg_7d", 
    "change_percent", "sma_7",
    "fear_greed_7d"
]

OPTIONAL_FEATURES = [
    "volume_avg_14d", "volume_avg_30d",
    "sma_14", "sma_30",
    "fear_greed_14d", "fear_greed_30d"
]

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def fetch_crypto_data(crypto_name):
    conn = get_connection()
    query = """
        SELECT *
        FROM crypto_prices
        WHERE crypto = %s
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(crypto_name,))
    conn.close()
    return df

def check_columns(df, required, optional):
    missing_required = [col for col in required if col not in df.columns or df[col].isnull().all()]
    missing_optional = [col for col in optional if col not in df.columns]
    return missing_required, missing_optional

def decide_action(last_price, predicted_price, threshold=0.01):
    delta = (predicted_price - last_price) / last_price
    if delta > threshold:
        return "BUY"
    elif delta < -threshold:
        return "SELL"
    else:
        return "HOLD"

def predict_model(crypto_name):
    df = fetch_crypto_data(crypto_name)
    missing_required, _ = check_columns(df, REQUIRED_FEATURES, OPTIONAL_FEATURES)
    if missing_required:
        raise Exception(f"Colonnes manquantes ou vides : {missing_required}")

    df = df.dropna(subset=REQUIRED_FEATURES)
    used_features = REQUIRED_FEATURES + [
        col for col in OPTIONAL_FEATURES if col in df.columns and not df[col].isnull().all()
    ]

    df["target"] = df["price"].shift(-1)
    y = df["target"].dropna()
    X = df[used_features].iloc[:-1, :]

    if len(X) < 2 or len(y) == 0:
        raise ValueError("Pas assez de données pour entraîner le modèle.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    latest_data = df.iloc[-1:][used_features]
    predicted_price = model.predict(latest_data)[0]
    last_price = df["price"].iloc[-1]
    decision = decide_action(last_price, predicted_price)

    return round(predicted_price, 2), decision, round(mae, 2)
