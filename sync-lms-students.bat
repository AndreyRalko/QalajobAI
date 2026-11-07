@echo off
cd /d "%~dp0"
title QalaJob AI - LMS student sync

echo ========================================
echo  QalaJob AI - LMS student sync
echo ========================================
echo.
echo  Open SSH tunnel first, then press a key.
echo  Example: ssh -L 6080:localhost:6080 user@lms-host
echo.
echo  Set LMS_* values in backend\.env before run.
echo.

cd /d "%~dp0backend"

set "PY="
if exist "venv\Scripts\python.exe" set "PY=venv\Scripts\python.exe"
if not defined PY if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY (
  echo [ERROR] venv python.exe not found. Create: python -m venv venv
  pause
  exit /b 1
)

set DJANGO_SETTINGS_MODULE=config.settings.server

echo Running: %PY% manage.py sync_lms_daily
echo.
"%PY%" manage.py sync_lms_daily
set ERR=%ERRORLEVEL%
echo.

if not "%ERR%"=="0" (
  echo [ERROR] Sync failed with code %ERR%.
) else (
  echo [OK] Sync finished.
)

echo.
pause
exit /b %ERR%
