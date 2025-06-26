#!/bin/bash

# Obtenir le répertoire du script et changer vers ce répertoire
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR" || {
    echo "❌ Erreur : Impossible de changer vers le répertoire du script."
    exit 1
}

# Créer l’environnement virtuel s’il n’existe pas
if [ ! -d ".venv" ]; then
    echo "🔧 Environnement virtuel non trouvé, création en cours..."
    python3 -m venv .venv || {
        echo "❌ Erreur : Impossible de créer l’environnement virtuel."
        exit 1
    }
fi

# Activer l’environnement virtuel
source .venv/bin/activate || {
    echo "❌ Erreur : Impossible d'activer l'environnement virtuel."
    exit 1
}

# Installation des dépendances
pip3 install -r requirements.txt

# Étape 1 - Lancer le bot
python bot.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'exécution de bot.py. Archivage et prédiction annulés."
    read -p "Appuyez sur Entrée pour continuer..."
    exit 1
fi

# Étape 2 - Archivage
python archive_and_clean.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'archivage."
    read -p "Appuyez sur Entrée pour continuer..."
fi

# Étape 3 - Génération des features (SMA, MACD, F&G, etc.)
python generate_features.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la génération des features."
    read -p "Appuyez sur Entrée pour continuer..."
    exit 1
fi

# Étape 4 - Vérification de la base de données
cd bdd || {
    echo "❌ Erreur : Répertoire bdd introuvable."
    exit 1
}
python check_db.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du check de la bdd."
    read -p "Appuyez sur Entrée pour continuer..."
fi
