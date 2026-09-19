@echo off
REM Confluence Backend Keep-Alive Auto-Prober
cd /d "%~dp0"
if exist "..\venv\Scripts\python.exe" (
    "..\venv\Scripts\python.exe" auto_prober.py %*
) else (
    python auto_prober.py %*
)
pause
