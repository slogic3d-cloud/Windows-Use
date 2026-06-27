@echo off
chcp 65001 > nul
title ZERO 2.0 — Desktop-Verknüpfung erstellen
cd /d "%~dp0"

:: Icon erstellen falls noch nicht vorhanden
if not exist "zero.ico" (
    python make_icon.py
)

:: Desktop-Verknüpfung via PowerShell erstellen
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$lnk = $ws.CreateShortcut($desktop + '\ZERO 2.0.lnk');" ^
  "$lnk.TargetPath = '%~dp0START_ZERO.bat';" ^
  "$lnk.IconLocation = '%~dp0zero.ico';" ^
  "$lnk.Description = 'ZERO 2.0 — S-LOGIC 3D KI-System starten';" ^
  "$lnk.WorkingDirectory = '%~dp0';" ^
  "$lnk.WindowStyle = 1;" ^
  "$lnk.Save();" ^
  "Write-Host 'Verknuepfung erstellt.'"

echo.
echo  [✓] Verknüpfung "ZERO 2.0" wurde auf dem Desktop erstellt.
echo  [✓] Icon: zero.ico
echo.
echo  Du kannst ERSTELLE_VERKNUEPFUNG.bat jetzt löschen.
echo.
pause
