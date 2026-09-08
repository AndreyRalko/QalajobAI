@echo off
chcp 65001 >nul
cd /d "%~dp0"
title QalaJob AI

echo ========================================
echo  QalaJob AI — запуск
echo  Frontend :3001  ^|  Backend :8088
echo ========================================
echo.

REM --- Проверка сборки ---
if not exist ".next\standalone\server.js" (
  echo [ERROR] Нет production-сборки.
  echo Сначала запустите build.bat, потом снова start.bat
  echo.
  pause
  exit /b 1
)

REM --- Static/public для standalone (нужны после каждого build) ---
if not exist ".next\standalone\.next" md ".next\standalone\.next"
if exist ".next\static" (
  robocopy ".next\static" ".next\standalone\.next\static" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
)
if exist "public" (
  robocopy "public" ".next\standalone\public" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
)

REM --- Освободить порты, если заняты ---
call :free_port 8088
call :free_port 3001

echo [1/2] Waitress на :8088 ...
start "QalaJob Backend :8088" /min "%~dp0start-backend.bat"
timeout /t 2 /nobreak >nul

cd /d "%~dp0"
set PORT=3001
set HOSTNAME=0.0.0.0

echo [2/2] Next.js на :3001 ...
echo.
echo  Сайт:  http://localhost:3001
echo  API:   http://localhost:8088/api/health/
echo.
echo  Закройте это окно или Ctrl+C — остановит фронт и бэкенд.
echo.

start "" "http://localhost:3001"
call npm run start:prod

echo.
echo Останавливаю backend на :8088 ...
call :free_port 8088
echo Готово.
pause
exit /b 0

:free_port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%~1" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a >nul 2>&1
)
exit /b 0
