@echo off
chcp 65001 >nul
cd /d "%~dp0"
title QalaJob Frontend :3001

if not exist ".next\standalone\server.js" (
  echo [ERROR] Нет production-сборки.
  echo Сначала запустите build.bat
  echo.
  pause
  exit /b 1
)

if not exist ".next\standalone\.next" md ".next\standalone\.next"
if exist ".next\static" (
  robocopy ".next\static" ".next\standalone\.next\static" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
)
if exist "public" (
  robocopy "public" ".next\standalone\public" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
)

set PORT=3001
set HOSTNAME=0.0.0.0

echo Starting Next.js on http://0.0.0.0:3001 ...
call npm run start:prod
echo.
pause
