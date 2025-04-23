from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sklearn.linear_model import LinearRegression
from utils.predict_model import predict_model


app = FastAPI()

class PredictRequest(BaseModel):
    crypto: str  # bitcoin, ethereum, etc.

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.post("/predict")
def predict(request: PredictRequest):
    try:
        prediction, decision, mae = predict_model(request.crypto)
        return {
            "prediction": prediction,
            "decision": decision,
            "model_mae": mae
        }
    except Exception as e:
        return {"error": str(e)}
