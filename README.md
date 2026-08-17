# QalaJob AI

Платформа вакансий с AI-функциями: **Next.js** + **Django REST Framework**.

## Стек

- **Frontend:** Next.js 16, React 19, Tailwind, next-intl
- **Backend:** Django 5, DRF, JWT, drf-spectacular
- **БД:** SQLite (dev) / PostgreSQL (prod)

## Быстрый запуск

Подробная пошаговая инструкция: **[SETUP.md](./SETUP.md)** (Ollama, гибрид AI, LMS sync).

```powershell
# 0 — Ollama + модель (один раз)
ollama pull qwen2.5:7b-instruct

# Terminal 1 — API
cd backend
.\venv\Scripts\Activate.ps1
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
