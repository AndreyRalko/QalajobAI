@echo off
cd /d "%~dp0"
title QalaJob AI

echo ========================================
echo  QalaJob AI - start
echo  Frontend :3001  ^|  Backend :8088
echo ========================================
echo.

REM --- Backend (background, same window) ---
cd /d "%~dp0backend"

if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
) else (
  echo [ERROR] venv not found. Create it first: python -m venv venv
  pause
  exit /b 1
)

if not exist "logs" md logs
if not exist "staticfiles" md staticfiles

set DJANGO_SETTINGS_MODULE=config.settings.server
set WAITRESS_HOST=0.0.0.0
set WAITRESS_PORT=8088

echo [1/2] Starting Waitress on :8088 ...
start /b python run_waitress.py > "logs\waitress-console.log" 2>&1
timeout /t 2 /nobreak >nul

REM --- Frontend (foreground) ---
cd /d "%~dp0"

if not exist ".next\BUILD_ID" (
  echo [ERROR] Production build not found.
  echo Run build.bat once, then start.bat again.
  echo.
  pause
  exit /b 1
)

echo [2/2] Starting Next.js on :3001 ...
echo.
echo Frontend: http://localhost:3001
echo Backend:  http://localhost:8088/api/health/
echo.
echo Close this window or press Ctrl+C to stop.
echo.

call npm run start:prod

echo.
echo Stopping backend on port 8088...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8088" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a >nul 2>&1
)

echo Stopped.
pause
