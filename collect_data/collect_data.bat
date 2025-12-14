@echo off
cd /d D:\Dev_web\dataScientest\cryptobot-backend
call .venv\Scripts\activate

:: Étape 1 - Lancer le bot
python bot.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de l'exécution de bot.py. Archivage et prédiction annulés.
    pause
    exit /b
)

:: Étape 2 - Archivage
python archive_and_clean.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de l'archivage.
    pause
)

:: Étape 3 - Génération des features (SMA, MACD, F&G, etc.)
python generate_features.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de la génération des features.
    pause
    exit /b
)

:: Étape 4 - check_db
cd bdd
python check_db.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors du check de la bdd.
    pause
)