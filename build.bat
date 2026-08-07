@echo off
cd /d "%~dp0"

echo ========================================
echo  QalaJob AI - one-time build
echo ========================================
echo.

if not exist ".env.production.local" (
  if exist ".env.production.example" (
    echo [WARN] .env.production.local missing.
    echo Copy .env.production.example to .env.production.local
    echo and set NEXT_PUBLIC_API_URL=http://YOUR_IP:8088/api/v1
    echo.
  )
)

echo Installing npm packages...
call npm install
if errorlevel 1 (
  echo [ERROR] npm install failed
  pause
  exit /b 1
)

echo.
echo Building Next.js...
call npm run build
if errorlevel 1 (
  echo [ERROR] npm run build failed
  pause
  exit /b 1
)

echo.
echo Backend: collectstatic...
cd backend
if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)
if not exist "logs" md logs
if not exist "staticfiles" md staticfiles
set DJANGO_SETTINGS_MODULE=config.settings.server
python manage.py collectstatic --noinput
cd ..

echo.
echo Done. Now run start.bat
pause
