#!/bin/bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Obtenir le répertoire du script et changer vers ce répertoire
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR" || exit 1

# Activer le fichier .env global (RDS credentials)
if [ -f ~/.cryptobot_env ]; then
    export $(grep -v '^#' ~/.cryptobot_env | xargs)
fi

# Créer le venv si inexistant
if [ ! -d ".venv" ]; then
    echo "🔧 Création du venv..."
    python3 -m venv .venv || exit 1
fi

# Activer le venv
source .venv/bin/activate || exit 1

# Installer dépendances
pip3 install -r requirements.txt --quiet

# Étape 1 — bot.py
echo "▶️  Exécution bot.py"
python3 bot.py
if [ $? -ne 0 ]; then
    echo "❌ bot.py a échoué"
    exit 1
fi

# Étape 2 — archivage
echo "📦 Archivage"
python3 archive_and_clean.py

# Étape 3 — features
echo "📊 Génération features"
python3 generate_features.py
if [ $? -ne 0 ]; then
    echo "❌ generate_features.py a échoué"
    exit 1
fi

# Étape 4 — check BDD
echo "🗄️ Vérification DB"
if [ -d "bdd" ]; then
    cd bdd
    python3 check_db.py
    cd ..
fi

echo "✅ Script CRON terminé"
