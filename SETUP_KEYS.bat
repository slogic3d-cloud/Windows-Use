@echo off
chcp 65001 > nul
title ZERO 2.0 — API Keys einrichten
cd /d "%~dp0"

cls
echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║       ZERO 2.0 — API Keys einrichten     ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Bestehende .env laden falls vorhanden
set ANTHROPIC_API_KEY=
set ELEVENLABS_API_KEY=
set WIX_API_KEY=
set WIX_ACCOUNT_ID=
set WIX_SITE_ID=
set OBSIDIAN_VAULT_PATH=

if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set "%%a=%%b"
    )
)

:: ── Anthropic ─────────────────────────────────────────────────
echo  ANTHROPIC API KEY
echo  Holen unter: https://console.anthropic.com/keys
echo  (beginnt mit sk-ant-...)
echo.
if not "%ANTHROPIC_API_KEY%"=="" (
    echo  Aktuell: %ANTHROPIC_API_KEY:~0,20%...
    echo  Leer lassen = unveraendert behalten
    echo.
)
set /p NEW_ANTHROPIC=  Anthropic Key eingeben:
if not "%NEW_ANTHROPIC%"=="" set ANTHROPIC_API_KEY=%NEW_ANTHROPIC%

echo.
echo  ─────────────────────────────────────────────
echo.

:: ── ElevenLabs (optional) ─────────────────────────────────────
echo  ELEVENLABS API KEY (optional — leer lassen fuer Browser-Stimme)
echo  Holen unter: https://elevenlabs.io/app/settings/api-keys
echo.
if not "%ELEVENLABS_API_KEY%"=="" (
    echo  Aktuell gesetzt.
)
set /p NEW_ELEVEN=  ElevenLabs Key eingeben (Enter = ueberspringen):
if not "%NEW_ELEVEN%"=="" set ELEVENLABS_API_KEY=%NEW_ELEVEN%

echo.
echo  ─────────────────────────────────────────────
echo.

:: ── Wix (optional) ────────────────────────────────────────────
echo  WIX SHOP KEYS (optional — fuer S-LOGIC 3D Bestellungen)
echo.
if not "%WIX_API_KEY%"=="" (
    echo  Aktuell gesetzt.
    set /p SKIP_WIX=  Wix-Keys aendern? (j/n):
    if /i "%SKIP_WIX%"=="j" goto :wix_input
    goto :obsidian
)
set /p SKIP_WIX=  Wix-Keys jetzt eingeben? (j/n):
if /i "%SKIP_WIX%"=="j" goto :wix_input
goto :obsidian

:wix_input
set /p NEW_WIX_KEY=  Wix API Key:
if not "%NEW_WIX_KEY%"=="" set WIX_API_KEY=%NEW_WIX_KEY%
set /p NEW_WIX_ACC=  Wix Account ID:
if not "%NEW_WIX_ACC%"=="" set WIX_ACCOUNT_ID=%NEW_WIX_ACC%
set /p NEW_WIX_SITE=  Wix Site ID:
if not "%NEW_WIX_SITE%"=="" set WIX_SITE_ID=%NEW_WIX_SITE%

:obsidian
echo.
echo  ─────────────────────────────────────────────
echo.

:: ── Obsidian (optional) ───────────────────────────────────────
echo  OBSIDIAN VAULT PFAD (optional — fuer Memory-Logging)
echo  Beispiel: C:\Users\Marius\Documents\ObsidianVault
echo.
if not "%OBSIDIAN_VAULT_PATH%"=="" (
    echo  Aktuell: %OBSIDIAN_VAULT_PATH%
)
set /p NEW_OBS=  Obsidian Pfad eingeben (Enter = ueberspringen):
if not "%NEW_OBS%"=="" set OBSIDIAN_VAULT_PATH=%NEW_OBS%

:: ── .env Datei schreiben ──────────────────────────────────────
echo.
echo  Speichere .env ...

(
echo # ZERO 2.0 — Konfiguration
echo # Erstellt von SETUP_KEYS.bat
echo.
echo ANTHROPIC_API_KEY=%ANTHROPIC_API_KEY%
echo ELEVENLABS_API_KEY=%ELEVENLABS_API_KEY%
echo WIX_API_KEY=%WIX_API_KEY%
echo WIX_ACCOUNT_ID=%WIX_ACCOUNT_ID%
echo WIX_SITE_ID=%WIX_SITE_ID%
echo OBSIDIAN_VAULT_PATH=%OBSIDIAN_VAULT_PATH%
) > .env

:: ── Prüfen ob Pflicht-Key gesetzt ────────────────────────────
if "%ANTHROPIC_API_KEY%"=="" (
    echo.
    echo  [!] WARNUNG: Kein Anthropic API Key gesetzt.
    echo      ZERO kann ohne diesen Key nicht starten.
    echo.
) else (
    echo  [✓] Anthropic Key gesetzt
)

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║             .env gespeichert!            ║
echo  ╚═══════════════════════════════════════════╝
echo.
echo  Starte jetzt ZERO 2.0 mit der Desktop-Verknuepfung
echo  oder mit START_ZERO.bat
echo.
pause
