@echo off
setlocal
echo ==========================================
echo   CycloRent - Système de Location
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Python depuis python.org
    pause
    exit /b 1
)

:: Check for Django and dependencies
echo [1/3] Verification des dependances...
if exist requirements.txt (
    echo Installation des dependances depuis requirements.txt...
    python -m pip install -r requirements.txt
) else (
    python -c "import django" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installation de Django...
        python -m pip install django
    ) else (
        echo Django est deja installe.
    )
)

:: Run migrations
echo [2/3] Migration de la base de donnees...
python manage.py migrate

:: Start server and open browser
echo [3/3] Lancement du serveur...
echo Le serveur sera accessible sur http://127.0.0.1:8000/
echo.

:: Small delay to give the server time to start before opening browser
start "" "http://127.0.0.1:8000/"
python manage.py runserver
