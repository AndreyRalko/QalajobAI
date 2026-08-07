@echo off
setlocal
cd /d "%~dp0"

echo Starting Next.js on http://0.0.0.0:3001 ...
call npm run start:prod
pause
