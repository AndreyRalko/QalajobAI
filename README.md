# QalaJob AI

Платформа вакансий с AI-функциями: **Next.js** + **Django REST Framework**.

## Стек

- **Frontend:** Next.js 16, React 19, Tailwind, next-intl
- **Backend:** Django 5, DRF, JWT, drf-spectacular
- **БД:** SQLite (dev) / PostgreSQL (prod, Docker)

## Быстрый запуск

Подробно: **[SETUP.md](./SETUP.md)**.

```powershell
# Terminal 1 — API
cd backend
.\venv\Scripts\Activate.ps1   # или: python -m venv venv && pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Terminal 2 — UI
cd ..
npm install
npm run dev
```

- UI: http://localhost:3000  
- API health: http://127.0.0.1:8000/api/health/  
- Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/

## Docker

```powershell
docker compose up --build
```

Нужен `backend/.env` — см. [SETUP.md](./SETUP.md).
