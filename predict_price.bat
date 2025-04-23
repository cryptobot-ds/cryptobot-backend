@echo off
cd /d D:\Dev_web\dataScientest\cryptobot-backend
call .venv\Scripts\activate

:: Étape 1 - Prédiction
python predict_price.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de la prédiction.
    pause
    exit /b
)

:: Étape 2 - Dashboard
cd dashboard
streamlit run dashboard.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de l'exécution de dashboard.py.
    pause
)

echo ✅ Script terminé avec succès !
timeout /t 60 /nobreak > NUL

