@echo off
cd /d "%~dp0"

echo ========================================
echo  QalaJob AI - start
echo  Frontend :3001  ^|  Backend :8088
echo ========================================
echo.

start "QalaJob Backend" cmd /k call "%~dp0start-backend.bat"
timeout /t 2 /nobreak >nul
start "QalaJob Frontend" cmd /k call "%~dp0start-frontend.bat"

echo Backend and frontend started in separate windows.
echo Frontend: http://localhost:3001
echo Backend:  http://localhost:8088/api/health/
echo.
pause
