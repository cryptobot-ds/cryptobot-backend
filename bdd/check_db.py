import psycopg2
import os
from dotenv import load_dotenv
import logging

# Charger les variables .env
# load_dotenv()
load_dotenv(dotenv_path=os.path.expanduser("~/.cryptobot_env"))
print("Connexion à la base :", os.getenv("DB_NAME"), os.getenv("DB_USER"))

# Configuration des logs
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/db_status.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_db_status():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        query = """
        SELECT crypto,
               MIN(timestamp) AS premiere_date,
               MAX(timestamp) AS derniere_date,
               COUNT(*) AS nombre_de_lignes
        FROM crypto_prices
        GROUP BY crypto;
        """

        cur.execute(query)
        results = cur.fetchall()

        logging.info("===== Statut de la table crypto_prices =====")
        for row in results:
            crypto, first_date, last_date, count = row
            logging.info(f"{crypto.upper()} | Début: {first_date} | Fin: {last_date} | Nombre de lignes: {count}")
        logging.info("============================================")

        cur.close()
        conn.close()
        print("✅ Check BDD terminé. Statut écrit dans logs/db_status.log.")

    except Exception as e:
        logging.error(f"Erreur lors du check DB : {e}")
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    check_db_status()
