#!/bin/bash

# Obtenir le répertoire du script et changer vers ce répertoire
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR" || {
    echo "❌ Erreur : Impossible de changer vers le répertoire du script."
    exit 1
}

# Activer l'environnement virtuel
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "❌ Erreur : .venv introuvable à la racine du projet."
    exit 1
fi

# Étape 1 - Prédiction
echo -e "\n▶️ Lancement de la prédiction..."
python predict_price.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la prédiction."
    exit 1
fi

# Étape 2 - Dashboard
# cd dashboard || exit 1
# echo -e "\n▶️ Lancement du dashboard Streamlit..."
# streamlit run dashboard.py
# if [ $? -ne 0 ]; then
#     echo "❌ Erreur lors de l'exécution de dashboard.py."
#     exit 1
# fi

echo -e "\n✅ SPrédiction ML terminée."

# Attente de 60 secondes avant de se fermer
sleep 60