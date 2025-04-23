import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import os
import time
import logging

# model de linear regression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'bot.log')
# Configuration du logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')


# Liste des cryptos à prédire
cryptos = {
    "bitcoin": "btc",
    "ethereum": "eth",
    "binancecoin": "bnb"
}


# Fonction pour prendre une décision basée sur la prédiction
def decide_action(last_price, predicted_price, threshold=0.01):
    delta = (predicted_price - last_price) / last_price
    if delta > threshold:
        return "BUY"
    elif delta < -threshold:
        return "SELL"
    else:
        return "HOLD"

# Fonction pour entraîner et prédire
def predict_price(crypto_name, crypto_code):
    try:
        # Charger les données
        file_path = f"csv/{crypto_name}_features.csv"
        if not os.path.exists(file_path):
            logging.warning(f"Fichier introuvable : {file_path}")
            return
        
        df = pd.read_csv(file_path, sep=";", quotechar='"')
        # df = df.dropna()  # Nettoyage des données
        df = df.dropna(subset=[
            "price", "RSI", "MACD", "MACD_Signal", "MACD_Histogram", "SMA",
            "Upper_Band", "Lower_Band", "ADX", "Stoch_RSI", "Volume_Avg",
            "Fibo_23", "Fibo_38", "Fibo_50", "Fibo_61", "Fibo_78",
            "Volume_Avg_7d", "Change_Percent", "SMA_7", "Fear_Greed_7d"
        ])

        # Définir les features et la target
        features = ["price", "RSI", "MACD", "MACD_Signal", "MACD_Histogram", "SMA",
                    "Upper_Band", "Lower_Band", "ADX", "Stoch_RSI", "Volume_Avg",
                    "Fibo_23", "Fibo_38", "Fibo_50", "Fibo_61", "Fibo_78",
                    "Volume_Avg_7d", "Change_Percent", "SMA_7", "Fear_Greed_7d"
                    ]
        print("✅ Colonnes présentes dans le CSV :", df.columns.tolist())
        
        X = df[features]

        # Définir la target = prix du jour suivant
        df["target"] = df["price"].shift(-1)
        y = df["target"].dropna()
        X = X.iloc[:-1, :]  # Aligner X avec y

        # Vérification des données
        if len(X) == 0 or len(y) == 0:
            logging.warning(f"Données insuffisantes pour {crypto_name}")
            return

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

        # Entraîner le modèle
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Prédictions et calcul de l'erreur
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        # Prédire le prix du lendemain
        latest_data = df.iloc[-1:][features]
        predicted_price = model.predict(latest_data)[0]
        last_price = df["price"].iloc[-1]
                
        # Décision simple
        decision = decide_action(last_price, predicted_price)

        # Sauvegarder la prédiction
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        prediction_result = pd.DataFrame({
            "timestamp": [timestamp],
            "predicted_price_tomorrow": [predicted_price],
            "last_price": [last_price],
            "model_mae": [mae],
            "decision": [decision]
        })

        os.makedirs("csv", exist_ok=True)
        prediction_file = f"csv/prediction_{crypto_code}.csv"
        prediction_result.to_csv(prediction_file, index=False, sep=";")

        # print(f" Prédiction {crypto_name.upper()} : {predicted_price:.2f} USD (MAE: {mae:.2f})")
        # logging.info(f"Prédiction {crypto_name.upper()} pour demain : {predicted_price:.2f} USD (MAE: {mae:.2f})")

        message = f"Prédiction {crypto_name.upper()} : {predicted_price:.2f} USD (MAE: {mae:.2f}) - Decision: {decision}"
        print(message)
        logging.info(message)


    except Exception as e:
        logging.error(f"Erreur lors de la prédiction de {crypto_name} : {e}")
        print(f" Erreur sur {crypto_name} : {e}")

# Exécuter la prédiction pour chaque crypto
for name, code in cryptos.items():
    predict_price(name, code)

    






