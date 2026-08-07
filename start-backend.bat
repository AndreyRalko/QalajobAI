@echo off
cd /d "%~dp0backend"

if exist "venv\Scripts\activate.bat" goto activate_venv
if exist ".venv\Scripts\activate.bat" goto activate_dotvenv
echo [ERROR] venv not found. Create it first: python -m venv venv
pause
exit /b 1

:activate_venv
call "venv\Scripts\activate.bat"
goto after_activate

:activate_dotvenv
call ".venv\Scripts\activate.bat"
goto after_activate

:after_activate
if not exist "logs" md logs
if not exist "staticfiles" md staticfiles

set DJANGO_SETTINGS_MODULE=config.settings.server
set WAITRESS_HOST=0.0.0.0
set WAITRESS_PORT=8088

echo Starting Waitress on http://0.0.0.0:8088 ...
python run_waitress.py
echo.
pause
