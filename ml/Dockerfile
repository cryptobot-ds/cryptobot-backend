# ml/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# copie le requirements.txt de la racine
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copie tout le projet
COPY . .

# Par défaut : lancer la prédiction
CMD ["python", "-m", "ml.predict_price"]
