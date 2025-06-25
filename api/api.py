from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sklearn.linear_model import LinearRegression
from utils.predict_model import predict_model
import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables .env
load_dotenv()

# Connexion à PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# on lance FastAPI avec  uvicorn api.api:app --reload
app = FastAPI()

class PredictRequest(BaseModel):
    crypto: str  # bitcoin, ethereum, etc.

def get_last_prediction(crypto_name):
    conn = get_connection()
    query = """
        SELECT predicted_price, decision, model_mae
        FROM predictions
        WHERE crypto = %s
        ORDER BY timestamp DESC
        LIMIT 1;
    """
    df = pd.read_sql_query(query, conn, params=(crypto_name,))
    conn.close()
    if not df.empty:
        return df.iloc[0]["predicted_price"], df.iloc[0]["decision"], df.iloc[0]["model_mae"]
    else:
        raise Exception("Pas de prédiction disponible en base")


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.post("/predict")
def predict(request: PredictRequest):
    try:
        prediction, decision, mae = get_last_prediction(request.crypto)
        return {
            "prediction": prediction,
            "decision": decision,
            "model_mae": mae
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/history/{crypto_name}")
def history(crypto_name: str):
    try:
        conn = get_connection()
        query = """
            SELECT timestamp, predicted_price, last_price, decision, model_mae
            FROM predictions
            WHERE crypto = %s
            ORDER BY timestamp DESC
            LIMIT 100;
        """
        df = pd.read_sql_query(query, conn, params=(crypto_name,))
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}


@app.post("/predict/live")
def predict_live(request: PredictRequest):
    prediction, decision, mae = predict_model(request.crypto)
    return {
        "prediction": prediction,
        "decision": decision,
        "model_mae": mae
    }
