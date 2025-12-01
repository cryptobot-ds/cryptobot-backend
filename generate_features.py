import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path


# Charger les variables .env
# load_dotenv()
# Charger les variables d'environnement depuis le fichier .env a la racine du serveur
load_dotenv(dotenv_path=os.path.expanduser("~/.cryptobot_env"))


# BASE_DIR = Path(__file__).resolve().parent
# load_dotenv(BASE_DIR / ".env")
print("Connexion à la base :", os.getenv("DB_NAME"), os.getenv("DB_USER"))

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )



cryptos = ["bitcoin", "ethereum", "binancecoin"]

def get_avg_fear_greed(days):
    conn = get_connection()
    query = """
        SELECT AVG(value) AS avg_fng
        FROM (
            SELECT value
            FROM fear_greed_index
            ORDER BY date DESC
            LIMIT 7
        ) sub;
    """
    df = pd.read_sql_query(query, conn, params=(days,))
    conn.close()
    return df["avg_fng"].iloc[0]

avg_fng_7d = get_avg_fear_greed(7)
avg_fng_14d = get_avg_fear_greed(14)
avg_fng_30d = get_avg_fear_greed(30)

print(f"✅ Moyenne Fear & Greed 7j : {avg_fng_7d}, 14j : {avg_fng_14d}, 30j : {avg_fng_30d}")

def insert_into_db(df, crypto):
    conn = get_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO crypto_prices (
            crypto, timestamp, price, volume, rsi, macd, sma,
            macd_signal, macd_histogram, upper_band, lower_band, adx, stoch_rsi,
            fibo_23, fibo_38, fibo_50, fibo_61, fibo_78,
            volume_avg_7d, volume_avg_14d, volume_avg_30d,
            sma_7, sma_14, sma_30,
            fear_greed_7d, fear_greed_14d, fear_greed_30d,
            change_percent
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s
        )
        ON CONFLICT (crypto, timestamp) DO UPDATE SET
            volume_avg_7d = EXCLUDED.volume_avg_7d,
            volume_avg_14d = EXCLUDED.volume_avg_14d,
            volume_avg_30d = EXCLUDED.volume_avg_30d,
            sma_7 = EXCLUDED.sma_7,
            sma_14 = EXCLUDED.sma_14,
            sma_30 = EXCLUDED.sma_30,
            fear_greed_7d = EXCLUDED.fear_greed_7d,
            fear_greed_14d = EXCLUDED.fear_greed_14d,
            fear_greed_30d = EXCLUDED.fear_greed_30d,
            change_percent = EXCLUDED.change_percent;
        """

    for _, row in df.iterrows():
        cur.execute(insert_query, (
            crypto, row["timestamp"], row["price"], row["volume"], row["RSI"], row["MACD"], row["SMA"],
            row["MACD_Signal"], row["MACD_Histogram"], row["Upper_Band"], row["Lower_Band"], row["ADX"], row["Stoch_RSI"],
            row["Fibo_23"], row["Fibo_38"], row["Fibo_50"], row["Fibo_61"], row["Fibo_78"],
            row["Volume_Avg_7d"], row["Volume_Avg_14d"], row["Volume_Avg_30d"],
            row["SMA_7"], row["SMA_14"], row["SMA_30"],
            row["Fear_Greed_7d"], row["Fear_Greed_14d"], row["Fear_Greed_30d"],
            row["Change_Percent"]
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Données insérées dans la table crypto_prices pour {crypto}")

for crypto in cryptos:
    file_path = f"csv/{crypto}_prices_rsi.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé : {file_path}")
        continue

    df = pd.read_csv(file_path, sep=";", quotechar='"')
    # df = df.dropna()

    # Calcul des nouvelles features :
    df["Volume_Avg_7d"] = df["volume"].rolling(window=7).mean()
    df["Volume_Avg_14d"] = df["volume"].rolling(window=14).mean()
    df["Volume_Avg_30d"] = df["volume"].rolling(window=30).mean()
    df["Change_Percent"] = df["price"].pct_change() * 100
    df["SMA_7"] = df["price"].rolling(window=7).mean()
    df["SMA_14"] = df["price"].rolling(window=14).mean()
    df["SMA_30"] = df["price"].rolling(window=30).mean()
    df["Fear_Greed_7d"] = avg_fng_7d
    df["Fear_Greed_14d"] = avg_fng_14d
    df["Fear_Greed_30d"] = avg_fng_30d

    # Suppression des lignes où les nouvelles features sont incomplètes
    df = df.dropna(subset=[
        "Volume_Avg_7d", "Volume_Avg_14d", "Volume_Avg_30d",
        "Change_Percent", "SMA_7", "SMA_14", "SMA_30"
    ])

    output_path = f"csv/{crypto}_features.csv"
    df.to_csv(output_path, index=False, sep=";")
    print(f"✅ Features enregistrées dans {output_path}")

    insert_into_db(df, crypto)
    print(f"✅ Données insérées dans la base de données pour {crypto}")
