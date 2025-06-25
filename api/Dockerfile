FROM python:3.10-slim

WORKDIR /app

COPY api/ ./api/
COPY utils/ ./utils/
COPY api/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande de lancement de l'API
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
