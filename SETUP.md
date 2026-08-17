# QalaJob AI — инструкция по запуску

Монорепозиторий: **Next.js** (фронтенд) + **Django REST** (бэкенд).

Продукт сейчас сфокусирован на **AI-ассистенте для составления резюме**.

| Часть | Путь | Порт |
|--------|------|------|
| Frontend | корень репозитория | http://localhost:3000 |
| Backend API | `backend/` | http://127.0.0.1:8000 |

После входа пользователь попадает в `/dashboard/student/ai` (диалог + черновик резюме).

---

## Требования

- **Node.js** 20+ (npm)
- **Python** 3.11–3.14
- Windows: PowerShell; для активации venv может понадобиться:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```

---

## Быстрый старт (локально)

Нужны **два терминала**.

### 1. Backend

```powershell
cd backend

# один раз: создать venv и зависимости
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# логи (Django пишет в backend/logs/)
New-Item -ItemType Directory -Force -Path logs | Out-Null

python manage.py migrate
python manage.py createsuperuser   # опционально, для /admin/
python manage.py runserver
```

Проверка:

- Health: http://127.0.0.1:8000/api/health/
- Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/
- Admin: http://127.0.0.1:8000/admin/

Корень `/` отдаёт **404** — это нормально: HTML-страницы на фронте, API по путям выше.

`backend/.env` для локального SQLite **не обязателен** (есть defaults в settings).

### 2. Frontend

```powershell
cd ..   # корень репозитория
npm install
npm run dev
```

Открыть: http://localhost:3000

API по умолчанию: `http://localhost:8000/api/v1`  
(см. `src/lib/api.ts`, переменная `NEXT_PUBLIC_API_URL`).

Optional `.env.local` in the repo root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

AI keys go only in `backend/.env` (OpenAI via Django).

---

## Повторный запуск (уже настроено)

**Терминал 1 — backend**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Терминал 2 — frontend**

```powershell
npm run dev
```

---

## Полезные API-эндпоинты

| URL | Назначение |
|-----|------------|
| `/api/health/` | Проверка живости |
| `/api/v1/auth/login/` | Логин (JWT, предзагруженные аккаунты) |
| `/api/v1/auth/me/` | Текущий пользователь |
| `/api/schema/swagger-ui/` | Документация API |

---

## Опциональные интеграции

Для базового UI + auth + CRUD ключи **не нужны**.

| Переменная | Где | Зачем |
|------------|-----|--------|
| `OPENAI_API_KEY` | `backend/.env` | AI (все запросы через Django → OpenAI) |
| `OPENAI_MODEL` | `backend/.env` | Модель (default: `gpt-4o-mini`) |
| `STRIPE_*` | `backend/.env` | Не используется (всё бесплатно) |
| `REDIS_URL` | `backend/.env` | Cache / Celery (prod) |
| `DB_*` | `backend/.env` | Postgres вместо SQLite |

Пример `backend/.env` (production на сервере):

```env
SECRET_KEY=change-me
DJANGO_SETTINGS_MODULE=config.settings.prod
DB_ENGINE=django.db.backends.postgresql
DB_NAME=qalajob_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## Структура проекта

```
qalajob-ai/
├── src/                 # Next.js App Router (UI)
├── backend/
│   ├── apps/            # Django apps (users, vacancies, ai, …)
│   ├── config/          # settings, urls, wsgi
│   ├── manage.py
│   └── requirements.txt
├── package.json         # frontend
└── SETUP.md             # эта инструкция
```

Settings:

- `config.settings` / `config.settings.dev` — локальная разработка (SQLite, CORS open)
- `config.settings.server` — VPS / Waitress :8088 (см. `DEPLOY.md`)
- `config.settings.prod` — production (HTTPS + Postgres)

---

## Типичные проблемы

### `psycopg2-binary` / `Pillow`: build error, `pg_config` not found

На **Python 3.13** старые pinned-версии без wheel падают при сборке из исходников. В `requirements.txt` должны быть совместимые версии (например `psycopg2-binary>=2.9.10`, `Pillow>=11`). Либо используйте **Python 3.11/3.12**.

### 404 на `http://127.0.0.1:8000/`

Ожидаемо. Откройте `/api/health/` или фронт на `:3000`.

### Frontend не достучится до API

1. Backend запущен на `:8000`
2. `NEXT_PUBLIC_API_URL` указывает на `http://localhost:8000/api/v1`
3. После смены env перезапустите `npm run dev`

### `Activate.ps1` не запускается

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# или без активации:
.\venv\Scripts\python.exe manage.py runserver
```

### Нет папки `logs` / ошибки логирования

```powershell
New-Item -ItemType Directory -Force -Path backend\logs
```
