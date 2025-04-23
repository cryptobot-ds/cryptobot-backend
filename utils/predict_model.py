# utils/predict_model.py

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import os

def predict_model(crypto_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, "csv", f"{crypto_name}_features.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"⚠️ Le fichier {file_path} est introuvable.")

    df = pd.read_csv(file_path, sep=";", quotechar='"')
    df = df.dropna(subset=[
        "price", "RSI", "MACD", "MACD_Signal", "MACD_Histogram", "SMA",
        "Upper_Band", "Lower_Band", "ADX", "Stoch_RSI", "Volume_Avg",
        "Fibo_23", "Fibo_38", "Fibo_50", "Fibo_61", "Fibo_78",
        "Volume_Avg_7d", "Change_Percent", "SMA_7", "Fear_Greed_7d"
    ])

    features = ["price", "RSI", "MACD", "MACD_Signal", "MACD_Histogram", "SMA",
                "Upper_Band", "Lower_Band", "ADX", "Stoch_RSI", "Volume_Avg",
                "Fibo_23", "Fibo_38", "Fibo_50", "Fibo_61", "Fibo_78",
                "Volume_Avg_7d", "Change_Percent", "SMA_7", "Fear_Greed_7d"]

    df["target"] = df["price"].shift(-1)
    y = df["target"].dropna()
    X = df[features].iloc[:-1, :]

    if len(X) == 0 or len(y) == 0:
        raise ValueError("Pas assez de données pour entraîner le modèle.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    latest_data = df.iloc[-1:][features]
    predicted_price = model.predict(latest_data)[0]
    last_price = df["price"].iloc[-1]

    delta = (predicted_price - last_price) / last_price
    if delta > 0.01:
        decision = "BUY"
    elif delta < -0.01:
        decision = "SELL"
    else:
        decision = "HOLD"

    return round(predicted_price, 2), decision, round(mae, 2)
