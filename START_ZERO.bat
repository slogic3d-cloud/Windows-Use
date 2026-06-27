@echo off
chcp 65001 > nul
title ZERO 2.0 — S-LOGIC 3D
cd /d "%~dp0"

:: ── .env laden ───────────────────────────────────────────────
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set "%%a=%%b"
    )
)

:: ── Icon erstellen falls noch nicht vorhanden ─────────────────
if not exist "zero.ico" (
    python make_icon.py > nul 2>&1
)

:: ── ASCII-Banner ──────────────────────────────────────────────
cls
echo.
echo     ███████╗███████╗██████╗  ██████╗     ██████╗    ██████╗
echo     ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗    ╚════██╗  ██╔═══██╗
echo       ███╔╝ █████╗  ██████╔╝██║   ██║     █████╔╝  ██║   ██║
echo      ███╔╝  ██╔══╝  ██╔══██╗██║   ██║     ╚═══██╗  ██║   ██║
echo     ███████╗███████╗██║  ██║╚██████╔╝    ██████╔╝  ╚██████╔╝
echo     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝     ╚═════╝    ╚═════╝
echo.
echo      S - L O G I C  3 D  —  Persönliches KI-Agentensystem
echo      ═══════════════════════════════════════════════════════
echo.

:: ── Port prüfen ob bereits belegt ────────────────────────────
netstat -an | find "8765" | find "LISTENING" > nul 2>&1
if %errorlevel%==0 (
    echo      [!] Port 8765 läuft bereits — öffne Browser...
    timeout /t 1 /nobreak > nul
    start http://localhost:8765
    echo.
    echo      ZERO 2.0 ist bereits aktiv: http://localhost:8765
    echo      Dieses Fenster kann geschlossen werden.
    pause
    exit /b
)

:: ── Server starten ────────────────────────────────────────────
echo      Starte ZERO 2.0 Server...
start /B "" python -m uvicorn zero.server:app --host 0.0.0.0 --port 8765 --log-level warning

:: ── Warten bis Server bereit ──────────────────────────────────
echo      Initialisiere...
:wait_loop
timeout /t 1 /nobreak > nul
netstat -an | find "8765" | find "LISTENING" > nul 2>&1
if not %errorlevel%==0 goto wait_loop

:: ── Browser öffnen ────────────────────────────────────────────
echo.
echo      [✓] ZERO 2.0 läuft auf http://localhost:8765
echo      [✓] iPad / Tailscale: http://%COMPUTERNAME%:8765
echo.
echo      Sage "ZERO"       → Spracheingabe aktivieren
echo      Sage "Kryptonit"  → Alle Aktionen sofort stoppen
echo.
echo      ═══════════════════════════════════════════════════════
echo      Server aktiv — dieses Fenster NICHT schließen
echo      ═══════════════════════════════════════════════════════
echo.

start http://localhost:8765
pause
