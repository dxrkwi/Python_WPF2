@echo off
REM Setup Virtual Environment für Python_WPF_2
REM Dieses Script erstellt ein venv und installiert alle Dependencies

echo.
echo === Python Virtual Environment Setup ===
echo.

REM 1. Virtuelle Umgebung erstellen
echo Erstelle virtuelles Environment in './venv'...
python -m venv venv

if errorlevel 1 (
    echo Fehler beim Erstellen von venv
    pause
    exit /b 1
)

echo venv erfolgreich erstellt
echo.

REM 2. venv aktivieren
echo Aktiviere virtuelles Environment...
call .\venv\Scripts\activate.bat

REM 3. pip upgrade
echo Upgrade pip...
python -m pip install --upgrade pip

echo.
echo Installiere Dependencies aus requirements.txt...
pip install -r .\requirements.txt

if errorlevel 1 (
    echo Fehler beim Installieren der Dependencies
    pause
    exit /b 1
)

echo.
echo === Setup abgeschlossen ===
echo Das venv ist aktiviert. Zum Deaktivieren: deactivate
echo.
pause
