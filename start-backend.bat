@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
title QalaJob Backend :8088

if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
) else (
  echo [ERROR] venv не найден.
  pause
  exit /b 1
)

if not exist "logs" md logs
set DJANGO_SETTINGS_MODULE=config.settings.server
set WAITRESS_HOST=0.0.0.0
set WAITRESS_PORT=8088
python manage.py collectstatic --noinput >nul
echo Starting Waitress on http://0.0.0.0:8088 ...
python run_waitress.py
echo.
pause
