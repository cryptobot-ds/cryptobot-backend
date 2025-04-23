# Réinstallation après pull

## Unix (MacOS/Linux)

**S'assurer que PostgreSQL est installé sur la machine :**

- MacOS avec [Homebrew](https://brew.sh/) : `brew install postgresql@17`
- Sur Ubuntu et dérivés : `sudo apt update && sudo apt install -y postgresql postgresql-contrib libpq-dev`
   
**Installer les dépendances :**

Script shell qui supprime le `.venv` et le recréé en installant les dépendances à partir du `requirements.txt` :

```shell
chmod +x setup_venv.sh
./setup_venv.sh
```

Si erreur avec `pg_config` sur Mac :

```shell
# S'assurer que pg_config est bien présent :
brew list postgresql@17 | grep pg_config

# L'ajouter au $PATH :
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
source ~/.zshrc
```

