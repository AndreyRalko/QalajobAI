# QalaJob AI

Платформа карьеры для студентов: **Django monolith** (HTML + REST API).

> Папка `src/` (Next.js) — устаревший фронт, в запуске не используется.

## Стек

- **UI:** Django templates + static CSS/JS (`apps.web`)
- **API:** Django REST Framework (session + JWT) под `/api/v1/`
- **БД:** SQLite
- **Сервер:** Waitress `:8088`

## Быстрый запуск

Двойной клик **`start.bat`** или:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py collectstatic --noinput
python run_waitress.py
```

- Сайт: http://localhost:8088  
- Вход: http://localhost:8088/login/  
- API health: http://localhost:8088/api/health/  
- Django Admin: http://localhost:8088/admin/

Логин студента: `Иванов_Иван` / `Student123`

Подробнее: **[SETUP.md](./SETUP.md)**, деплой: **[DEPLOY.md](./DEPLOY.md)**.
