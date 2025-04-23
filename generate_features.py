import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables .env
load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

cryptos = ["bitcoin", "ethereum", "binancecoin"]

def get_avg_fear_greed():
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
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df["avg_fng"].iloc[0]

avg_fng_7d = get_avg_fear_greed()
print(f"✅ Moyenne Fear & Greed des 7 derniers jours : {avg_fng_7d}")

for crypto in cryptos:
    file_path = f"csv/{crypto}_prices_rsi.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé : {file_path}")
        continue

    df = pd.read_csv(file_path, sep=";", quotechar='"')
    df = df.dropna()

    # Calcul des nouvelles features :
    df["Volume_Avg_7d"] = df["volume"].rolling(window=7).mean()
    df["Change_Percent"] = df["price"].pct_change() * 100
    df["SMA_7"] = df["price"].rolling(window=7).mean()
    df["Fear_Greed_7d"] = avg_fng_7d  # Valeur réelle depuis la BDD

    df = df.dropna()

    output_path = f"csv/{crypto}_features.csv"
    df.to_csv(output_path, index=False, sep=";")
    print(f"✅ Features enregistrées dans {output_path}")
