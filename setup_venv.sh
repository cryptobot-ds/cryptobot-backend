#!/bin/bash

# Supprimer l'ancien environnement virtuel (si nécessaire)
rm -rf .venv

# Créer un nouvel environnement virtuel
python3 -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation (optionnel)
pip list