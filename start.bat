@echo off
chcp 65001 >nul
cd /d "%~dp0"
title QalaJob AI (Django)

echo ========================================
echo  QalaJob AI — Django monolith
echo  http://localhost:8088
echo ========================================
echo.

call :free_port 8088

cd /d "%~dp0backend"

if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
) else (
  echo [ERROR] venv не найден. Создайте: python -m venv venv
  pause
  exit /b 1
)

if not exist "logs" md logs
if not exist "staticfiles" md staticfiles

set DJANGO_SETTINGS_MODULE=config.settings.server
set WAITRESS_HOST=0.0.0.0
set WAITRESS_PORT=8088

echo Collectstatic...
python manage.py collectstatic --noinput >nul

echo Starting Waitress on :8088 ...
echo.
echo  Сайт:   http://localhost:8088
echo  Вход:   http://localhost:8088/login/
echo  API:    http://localhost:8088/api/health/
echo  Admin:  http://localhost:8088/admin/
echo.
echo  Ctrl+C — остановить.
echo.

start "" "http://localhost:8088"
python run_waitress.py

echo.
pause
exit /b 0

:free_port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%~1" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a >nul 2>&1
)
exit /b 0
