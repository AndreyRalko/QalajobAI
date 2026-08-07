@echo off
cd /d "%~dp0"

if not exist ".next\BUILD_ID" (
  echo [ERROR] Production build not found.
  echo Run build.bat once, then start.bat again.
  echo.
  pause
  exit /b 1
)

echo Starting Next.js on http://0.0.0.0:3001 ...
call npm run start:prod
echo.
pause
