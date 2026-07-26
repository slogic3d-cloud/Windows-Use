@echo off
chcp 65001 > nul
title ZERO 2.0 — Installation
cd /d "%~dp0"

cls
echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║       ZERO 2.0 — Erstinstallation        ║
echo  ║           S-LOGIC 3D Setup               ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: ── Python prüfen ────────────────────────────────────────────
echo  [1/5] Python wird geprüft...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [FEHLER] Python nicht gefunden!
    echo  Bitte Python 3.10+ installieren:
    echo  https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [✓] %PY_VER% gefunden

:: ── pip upgrade ───────────────────────────────────────────────
echo.
echo  [2/5] pip wird aktualisiert...
python -m pip install --upgrade pip --quiet
echo  [✓] pip aktuell

:: ── Pakete installieren ───────────────────────────────────────
echo.
echo  [3/5] ZERO 2.0 Pakete werden installiert...
echo        (kann 2-5 Minuten dauern)
echo.
pip install -e ".[zero]" --quiet
if %errorlevel% neq 0 (
    echo  [FEHLER] Installation fehlgeschlagen. Bitte Fehlermeldung prüfen.
    pause
    exit /b 1
)
pip install python-docx openpyxl --quiet
echo  [✓] Alle Pakete installiert

:: ── .env erstellen ────────────────────────────────────────────
echo.
echo  [4/5] Konfiguration wird geprüft...
if not exist ".env" (
    copy ".env.example" ".env" > nul
    echo  [!] .env wurde erstellt — BITTE JETZT AUSFÜLLEN:
    echo.
    echo      Öffne die Datei ".env" im Hauptordner
    echo      und trage deine API-Keys ein.
    echo.
    echo      PFLICHT:  ANTHROPIC_API_KEY
    echo      PFLICHT:  ELEVENLABS_API_KEY
    echo.
    start notepad ".env"
) else (
    echo  [✓] .env bereits vorhanden
)

:: ── Icon + Verknüpfung ────────────────────────────────────────
echo.
echo  [5/5] Icon und Desktop-Verknüpfung werden erstellt...
python make_icon.py > nul 2>&1
if exist "zero.ico" (
    echo  [✓] zero.ico erstellt
) else (
    echo  [!] Icon konnte nicht erstellt werden (Pillow fehlt?) — kein Problem, weiter.
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$lnk = $ws.CreateShortcut($desktop + '\ZERO 2.0.lnk');" ^
  "$lnk.TargetPath = '%~dp0START_ZERO.bat';" ^
  "$lnk.IconLocation = '%~dp0zero.ico';" ^
  "$lnk.Description = 'ZERO 2.0 starten';" ^
  "$lnk.WorkingDirectory = '%~dp0';" ^
  "$lnk.WindowStyle = 1;" ^
  "$lnk.Save();" > nul 2>&1

echo  [✓] Desktop-Verknüpfung "ZERO 2.0" erstellt

:: ── Fertig ────────────────────────────────────────────────────
echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║           Installation fertig!           ║
echo  ╚═══════════════════════════════════════════╝
echo.
echo  Was jetzt zu tun ist:
echo.
echo  1. .env öffnen und API-Keys eintragen
echo     (wurde gerade in Notepad geöffnet)
echo.
echo  2. Danach: "ZERO 2.0" auf dem Desktop starten
echo.
echo  iPad-Zugriff via Tailscale:
echo  http://%COMPUTERNAME%:8765
echo.
pause
