@echo off
setlocal
cd /d "%~dp0backend"

if exist "venv\Scripts\activate.bat" (
  call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
  call .venv\Scripts\activate.bat
) else (
  echo [ERROR] venv not found. Create it first: python -m venv venv
  pause
  exit /b 1
)

set DJANGO_SETTINGS_MODULE=config.settings.server
set WAITRESS_HOST=0.0.0.0
set WAITRESS_PORT=8088

echo Starting Waitress on http://0.0.0.0:8088 ...
python run_waitress.py
pause
