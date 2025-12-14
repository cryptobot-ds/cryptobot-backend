#!/bin/bash
set -euo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

METRICS_DIR="/var/lib/node_exporter/textfile_collector"
METRICS_FILE="$METRICS_DIR/cryptobot_cron.prom"

# --- fonctions métriques ---
write_success() {
  mkdir -p "$METRICS_DIR"
  cat > "$METRICS_FILE" <<EOF
cryptobot_cron_last_success_timestamp $(date +%s)
cryptobot_cron_last_run_status 1
EOF
}

write_failure() {
  mkdir -p "$METRICS_DIR"
  cat > "$METRICS_FILE" <<EOF
cryptobot_cron_last_failure_timestamp $(date +%s)
cryptobot_cron_last_run_status 0
EOF
}

# si n'importe quoi échoue -> on écrit failure
trap 'echo "❌ CRON error (line $LINENO)"; write_failure' ERR

# --- se placer dans le dossier du script ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"


# --- charger env RDS ---
if [ -f "$HOME/.cryptobot_env" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.cryptobot_env"
  set +a
fi

# --- venv ---
if [ ! -d ".venv" ]; then
  echo "🔧 Création du venv..."
  python3 -m venv .venv
fi

# --- activer venv ---
# shellcheck disable=SC1091
source .venv/bin/activate

# --- deps ---
pip3 install -r requirements.txt --quiet

echo "▶️  Exécution bot.py"
python3 bot.py

echo "📦 Archivage"
python3 archive_and_clean.py

echo "📊 Génération features"
python3 generate_features.py

echo "🗄️ Vérification DB"
if [ -f "../bdd/check_db.py" ]; then
  python3 ../bdd/check_db.py
fi


echo "▶️ Lancement predict_price"
python3 ../ml/predict_price.py
echo "✅ Prédiction terminée"

# si tout est OK
write_success
echo "✅ Script CRON terminé"
