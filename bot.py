import requests
import pandas as pd
import numpy as np
import time
import os
from dotenv import load_dotenv
import csv  

# Charger les variables du fichier .env
# load_dotenv()

# Récupérer la clé API depuis le .env
# COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
# print(f" Clé API chargée : {COINGECKO_API_KEY}")

# Définir l'URL de base (Toujours API gratuite)
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Fonction pour récupérer les prix historiques depuis CoinGecko
def get_crypto_prices(crypto_id="bitcoin", currency="usd", days=30, interval="daily"):
    try:
        url = f"{COINGECKO_BASE_URL}/coins/{crypto_id}/market_chart"
        params = {
            "vs_currency": currency,
            "days": days,
            "interval": interval
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f" Erreur API CoinGecko ({crypto_id}): {response.status_code} - {response.text}")
            return pd.DataFrame()

        data = response.json()
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])

        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["volume"] = [v[1] for v in volumes]
        return df
    except Exception as e:
        print(f" Erreur lors de la récupération des prix historiques ({crypto_id}): {e}")
        return pd.DataFrame()

# Fonction pour récupérer le prix actuel depuis CoinGecko
def get_price_coingecko(crypto_id="bitcoin", currency="usd"):
    try:
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": crypto_id,
            "vs_currencies": currency
        }
        response = requests.get(url, params=params)

        if response.status_code == 429:
            print(f" code 429 Trop de requêtes vers CoinGecko. Attente de 30 secondes...")
            time.sleep(30)  # Pause pour éviter d'être bloqué
            return get_price_coingecko(crypto_id, currency)  # Retenter après 30s

        if response.status_code != 200:
            print(f" Erreur API CoinGecko ({crypto_id}): {response.status_code} - {response.text}")
            return None

        data = response.json()
        return data.get(crypto_id, {}).get(currency, None)
    except Exception as e:
        print(f" Erreur avec CoinGecko ({crypto_id}): {e}")
        return None

# Liste des cryptos
cryptos = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "binancecoin": "BNBUSDT"
}

df_dict = {}
price_data = []

# Récupération des prix historiques
for crypto in cryptos.keys():
    try:
        time.sleep(10)  # Pause pour éviter les blocages API
        df = get_crypto_prices(crypto_id=crypto, days=30)
        if df.empty:
            print(f" Aucune donnée reçue pour {crypto} depuis CoinGecko !")
        else:
            df.to_csv(f"{crypto}_prices_rsi.csv", index=False, sep=";")
            print(f"\n Prix récupérés pour {crypto.capitalize()}")
    except Exception as e:
        print(f" Erreur lors de la récupération des données pour {crypto}: {e}")

print("\n Les fichiers CSV contenant les prix ont été enregistrés.")

# Fonction pour récupérer le prix actuel depuis Binance
def get_price_binance(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f" Erreur avec Binance ({symbol}): {e}")
        return None

# Comparaison CoinGecko vs Binance
for coin, binance_symbol in cryptos.items():
    try:
        price_cg = get_price_coingecko(crypto_id=coin)
        time.sleep(3)  # Pause de 3 secondes entre les requêtes API CoinGecko et Binance
        price_bi = get_price_binance(symbol=binance_symbol)

        if price_cg is not None and price_bi is not None:
            diff_percent = ((price_bi - price_cg) / price_cg) * 100
            price_data.append([coin, price_cg, price_bi, diff_percent])

            print(f"{coin.capitalize()} - CoinGecko: ${price_cg:.2f}, Binance: ${price_bi:.2f} | Différence: {diff_percent:.2f}%")
        else:
            print(f" Impossible de récupérer le prix pour {coin}")
    except Exception as e:
        print(f" Erreur pour {coin}: {e}")

# Convertir les résultats en DataFrame
df_comparison = pd.DataFrame(price_data, columns=["Crypto", "CoinGecko Price", "Binance Price", "Difference (%)"])

# Sauvegarder les résultats dans un CSV
timestamp = time.strftime("%Y%m%d-%H%M%S")
filename = f"crypto_price_comparison_{timestamp}.csv"
df_comparison.to_csv(filename, index=False, sep=";")

print(f"\n Comparaison des prix enregistrée dans '{filename}' ")


# Fonctions d'analyse technique
def calculate_rsi(df, period=14):
    df["price_change"] = df["price"].diff(1)
    df["gain"] = np.where(df["price_change"] > 0, df["price_change"], 0)
    df["loss"] = np.where(df["price_change"] < 0, -df["price_change"], 0)

    #  Assurez-vous que `gain` et `loss` sont bien des Series avant `rolling()`
    df["gain"] = pd.Series(df["gain"])
    df["loss"] = pd.Series(df["loss"])

    avg_gain = df["gain"].rolling(window=period, min_periods=1).mean()
    avg_loss = df["loss"].rolling(window=period, min_periods=1).mean()

    df["RSI"] = 100 - (100 / (1 + avg_gain / (avg_loss + 1e-10)))  # Éviter division par 0
    return df



# Fonction pour récupérer le Fear & Greed Index
def get_fear_greed_index():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        return int(data["data"][0]["value"]), data["data"][0]["value_classification"]
    except Exception as e:
        print(f" Erreur lors de la récupération du Fear & Greed Index: {e}")
        return None, None


#  Fonction pour calculer les Bandes de Bollinger
def calculate_bollinger_bands(df, period=20, std_dev=2):
    df["SMA"] = df["price"].rolling(window=period).mean()  # Moyenne Mobile Simple
    df["STD"] = df["price"].rolling(window=period).std()   # Écart-Type
    df["Upper_Band"] = df["SMA"] + (df["STD"] * std_dev)   # Bande Supérieure
    df["Lower_Band"] = df["SMA"] - (df["STD"] * std_dev)   # Bande Inférieure
    return df


#  Fonction pour calculer la Moyenne Mobile Simple (SMA) et Exponentielle (EMA)
def calculate_moving_averages(df, period_sma=20, period_ema=20):
    df["SMA"] = df["price"].rolling(window=period_sma).mean()  # Moyenne Mobile Simple
    df["EMA"] = df["price"].ewm(span=period_ema, adjust=False).mean()  # Moyenne Mobile Exponentielle
    return df


# Fonction pour calculer le MACD
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df["EMA_12"] = df["price"].ewm(span=short_window, adjust=False).mean() 
    df["EMA_26"] = df["price"].ewm(span=long_window, adjust=False).mean() 
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=signal_window, adjust=False).mean() 
    df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

    return df

# Fonction pour calculer le stochastic_rs
def calculate_stochastic_rsi(df, period=14):
    df["RSI"] = calculate_rsi(df, period)["RSI"]

    #  Convertir en `pd.Series`
    df["RSI_Min"] = pd.Series(df["RSI"].rolling(window=period).min())
    df["RSI_Max"] = pd.Series(df["RSI"].rolling(window=period).max())

    df["Stoch_RSI"] = (df["RSI"] - df["RSI_Min"]) / (df["RSI_Max"] - df["RSI_Min"] + 1e-10) * 100
    return df


# Fonction pour calculer l adx
def calculate_adx(df, period=14):
    df["High_Low"] = df["price"].diff()

    df["pos_DI"] = pd.Series(np.where(df["High_Low"] > 0, df["High_Low"], 0)).rolling(window=period).mean()
    df["neg_DI"] = pd.Series(np.where(df["High_Low"] < 0, abs(df["High_Low"]), 0)).rolling(window=period).mean()
    
    df["DX"] = (abs(df["pos_DI"] - df["neg_DI"]) / (df["pos_DI"] + df["neg_DI"] + 1e-10)) * 100  # Éviter division par 0
    df["ADX"] = df["DX"].rolling(window=period).mean()
    return df



# Fonction pour calculer volume_average
def calculate_volume_average(df, period=14):
    df["Volume_Avg"] = df["volume"].rolling(window=period).mean()
    return df

#  Fonction pour calculer les niveaux de Fibonacci
def calculate_fibonacci_levels(df):
    high = df["price"].max()
    low = df["price"].min()
    levels = [0.236, 0.382, 0.5, 0.618, 0.786]

    for level in levels:
        df[f"Fibo_{int(level*100)}"] = low + (high - low) * level

    return df


# calcul du RSI et mise à jour des fichiers CSV
for coin in cryptos.keys():
    try:
        df = pd.read_csv(f"{coin}_prices_rsi.csv", sep=";")  # Charger les prix existants
        df = calculate_rsi(df)  # RSI
        df = calculate_stochastic_rsi(df)  # Stochastic RSI
        df = calculate_bollinger_bands(df)  # Bandes de Bollinger
        df = calculate_moving_averages(df)  # Moyennes Mobiles (SMA & EMA)
        df = calculate_macd(df)  # MACD
        df = calculate_adx(df)  # ADX
        df = calculate_volume_average(df)  # Volume Moyen
        df = calculate_fibonacci_levels(df)  # Niveaux de Fibonacci

        #  Ajouter le Fear & Greed Index
        fng_value, fng_classification = get_fear_greed_index()
        df["Fear_Greed_Index"] = fng_value
        df["Fear_Greed_Classification"] = fng_classification

        fng_value, fng_classification = get_fear_greed_index()
        df["Fear_Greed_Index"] = fng_value  # Ajout de la valeur du F&G Index dans chaque ligne du dataframe
        df["Fear_Greed_Classification"] = fng_classification


        #  Enregistrer le fichier CSV mis à jour avec RSI
        # df.to_csv(f"{coin}_prices_rsi.csv", index=False, sep=";")
        df.to_csv(f"{coin}_prices_rsi.csv", index=False, sep=";", quoting=csv.QUOTE_NONNUMERIC)

        print(f" {coin.capitalize()}  RSI ajouté et enregistré dans {coin}_prices_rsi.csv")

    except Exception as e:
        print(f" Erreur lors du calcul du RSI pour {coin}: {e}")

print("\n Calcul du RSI terminé et fichiers mis à jour.")