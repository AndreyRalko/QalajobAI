@echo off
chcp 65001 >nul
cd /d "%~dp0"
title QalaJob AI — LMS student sync

echo ========================================
echo  QalaJob AI — синхронизация студентов LMS
echo ========================================
echo.
echo  Запрос к LMS:
echo    SELECT Lastname, firstname, login, password
echo    FROM students WHERE isStudent = 1
echo    (+ StudentID — нужен для привязки аккаунта)
echo.
echo  Перед запуском откройте SSH-туннель, например:
echo    ssh -L 6080:localhost:6080 user@lms-host
echo.
echo  В backend\.env должны быть:
echo    LMS_SYNC_ENABLED=true
echo    LMS_MYSQL_HOST / PORT / DB / USER / PASSWORD
echo.

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

set DJANGO_SETTINGS_MODULE=config.settings.server

echo Запуск sync_lms_daily...
echo.
python manage.py sync_lms_daily
set ERR=%ERRORLEVEL%
echo.

if %ERR% neq 0 (
  echo [ERROR] Синхронизация завершилась с ошибкой ^(%ERR%^).
) else (
  echo [OK] Синхронизация завершена.
)

echo.
pause
exit /b %ERR%
