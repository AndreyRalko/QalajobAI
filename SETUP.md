# QalaJob AI — инструкция по запуску

Монорепозиторий: **Next.js** (фронтенд) + **Django REST** (бэкенд).

| Сервис | Путь / URL | Порт |
|--------|------------|------|
| Frontend (UI) | корень репозитория | http://localhost:3000 |
| Backend API | `backend/` | http://127.0.0.1:8000 |
| Ollama (локальный AI) | отдельное приложение | http://127.0.0.1:11434 |
| Redis (опционально) | для Celery / LMS sync | 6379 |

После входа студент попадает в `/dashboard/student/ai`.

---

## 1. Что нужно установить

| Компонент | Версия | Зачем |
|-----------|--------|--------|
| **Node.js** | 20+ | фронтенд |
| **Python** | 3.11–3.14 | бэкенд |
| **Ollama** | последняя | локальная модель Qwen2.5-7B |
| **Redis** | опционально | автосинхронизация LMS по расписанию |

Windows PowerShell — если venv не активируется:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## 2. Первый запуск (с нуля)

### Шаг 1 — Клонировать и открыть проект

```powershell
cd D:\projects\QalajobAI
```

### Шаг 2 — Backend: venv и зависимости

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
New-Item -ItemType Directory -Force -Path logs | Out-Null
```

Без активации venv можно так:

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

### Шаг 3 — Настроить `backend/.env`

Скопируйте пример ниже в `backend/.env` и подставьте свои ключи.
Файл **не коммитится** в git.

```env
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
TIME_ZONE=Asia/Qyzylorda

# OpenAI (облако: сложные задачи + fallback)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Гибрид: локальный Qwen + OpenAI
LLM_HYBRID_ENABLED=true
LLM_LOCAL_BASE_URL=http://127.0.0.1:11434/v1
LLM_LOCAL_API_KEY=ollama
LLM_LOCAL_MODEL=qwen2.5:7b-instruct
LLM_LOCAL_TIMEOUT=180
LLM_FALLBACK_TO_OPENAI=true
LLM_KK_USE_OPENAI=true
LLM_DEFAULT_PROVIDER=local

# HeadHunter (опционально, для поиска вакансий)
# HH_CLIENT_ID=...
# HH_CLIENT_SECRET=...

# LMS sync (опционально: сначала откройте туннель вручную)
# ssh -L 6080:localhost:6080 admin_kgu@192.168.10.2
# LMS_SYNC_ENABLED=true
# LMS_MYSQL_HOST=127.0.0.1
# LMS_MYSQL_PORT=6080
# LMS_MYSQL_DB=nitro
# LMS_MYSQL_USER=user
# LMS_MYSQL_PASSWORD=user
```

### Шаг 4 — Миграции БД

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

Используется **SQLite** (`backend/db.sqlite3`) — отдельная БД не нужна.

### Шаг 5 — Ollama и модель Qwen

1. Скачайте Ollama: https://ollama.com  
2. В терминале:

```powershell
ollama pull qwen2.5:7b-instruct
```

3. Проверка:

```powershell
curl http://127.0.0.1:11434/v1/models
```

Ollama на Windows обычно стартует сам в фоне после установки.

### Шаг 6 — Frontend

```powershell
cd D:\projects\QalajobAI
npm install
```

Опционально `.env.local` в корне:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 3. Ежедневный запуск

Нужно **минимум 2 терминала**. Ollama — если не запущен как служба.

### Терминал 1 — Ollama (если AI нужен)

```powershell
ollama serve
```

Или убедитесь, что модель на месте:

```powershell
ollama list
```

### Терминал 2 — Backend

```powershell
cd D:\projects\QalajobAI\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

Проверка:

- Health: http://127.0.0.1:8000/api/health/
- Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/
- Django Admin: http://127.0.0.1:8000/admin/

Корень `http://127.0.0.1:8000/` отдаёт **404** — это нормально.

### Терминал 3 — Frontend

```powershell
cd D:\projects\QalajobAI
npm run dev
```

Открыть: **http://localhost:3000**

---

## 4. Тестовые аккаунты

| Роль | Логин | Пароль |
|------|-------|--------|
| Студент | `Иванов_Иван` | `Student123` |
| Студент (тест, IT + транскрипт) | `Демо_Алина` | `Student123` |
| Работодатель | `Петров_Петр` | `Employer123` |
| Админ | `Сидоров_Админ` | `Admin1234` |

Админ-панель в UI (после входа под админом):

| Страница | URL |
|----------|-----|
| Пользователи | `/dashboard/admin/users` |
| AI логи | `/dashboard/admin/ai-logs` |
| LMS sync | `/dashboard/admin/lms-sync` |

---

## 5. Как работает AI (гибрид)

```
Запрос → Django → диспетчер → Local (Qwen) или OpenAI
                              ↓ ошибка
                         OpenAI (fallback)
```

| Задача | Куда идёт |
|--------|-----------|
| Ассистент, улучшение резюме | **Local** (Qwen) |
| Рекомендации вакансий, skill gap, match | **OpenAI** |
| Career coach / cover letter (ru, en) | **Local**, при сбое → OpenAI |
| Career coach на **kk** | **OpenAI** |

В `/dashboard/admin/ai-logs` видно поле **provider**: `local`, `openai` или `fallback`.

### Только OpenAI (без Ollama)

В `backend/.env`:

```env
LLM_HYBRID_ENABLED=false
```

### Только local (без fallback)

```env
LLM_HYBRID_ENABLED=true
LLM_FALLBACK_TO_OPENAI=false
```

---

## 6. LMS sync (опционально)

Синхронизация логинов/паролей студентов из MySQL вуза.
Код **не открывает** SSH-туннель сам — сначала откройте его вручную (как в AIScience), затем запустите команду.

### Шаг 1 — Открыть туннель вручную

```powershell
ssh -L 6080:localhost:6080 admin_kgu@192.168.10.2
```

Оставьте это окно открытым.

### Шаг 2 — Обновить логины и пароли

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py sync_lms_daily
```

В `backend/.env` должны быть:

```env
LMS_SYNC_ENABLED=true
LMS_MYSQL_HOST=127.0.0.1
LMS_MYSQL_PORT=6080
LMS_MYSQL_DB=nitro
LMS_MYSQL_USER=user
LMS_MYSQL_PASSWORD=user
```

### Автозапуск по расписанию

Нужны **Redis + Celery**, и к моменту запуска туннель уже должен быть открыт:

```powershell
# Терминал 4 — Redis (если установлен)
redis-server

# Терминал 5 — Celery worker + beat
cd backend
.\venv\Scripts\Activate.ps1
celery -A config worker -B -l info
```

Расписание настраивается в UI: `/dashboard/admin/lms-sync`.
---

## 7. Полезные команды

```powershell
# Тесты backend
cd backend
.\venv\Scripts\python.exe manage.py test apps.ai

# Создать суперпользователя Django
python manage.py createsuperuser

# Проверить локальную модель
curl http://127.0.0.1:11434/api/generate -d "{\"model\":\"qwen2.5:7b-instruct\",\"prompt\":\"Hello\",\"stream\":false}"
```

---

## 8. Типичные проблемы

### AI отвечает «Demo mode»

В `backend/.env` нет `OPENAI_API_KEY` и гибрид выключен (`LLM_HYBRID_ENABLED=false`).

### AI медленный или пустой ответ

1. Ollama запущен? `ollama list`
2. Модель скачана? `ollama pull qwen2.5:7b-instruct`
3. В логах admin → AI logs смотрите `provider` и `status`
4. При сбое local должен сработать fallback (`LLM_FALLBACK_TO_OPENAI=true`)

### Frontend не видит API

1. Backend на `:8000`
2. `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
3. Перезапустите `npm run dev` после смены env

### `Activate.ps1` не работает

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# или
.\venv\Scripts\python.exe manage.py runserver
```

### Ошибка `psycopg2` / `Pillow` при pip install

Используйте Python 3.11–3.12 или обновите `requirements.txt`.

### 404 на http://127.0.0.1:8000/

Нормально. Откройте фронт `:3000` или `/api/health/`.

---

## 9. Структура проекта

```
QalajobAI/
├── src/                    # Next.js (UI)
├── backend/
│   ├── apps/
│   │   ├── ai/             # AI + гибрид LLM
│   │   ├── lms_sync/       # синхронизация LMS
│   │   └── users/          # auth, preset users
│   ├── config/             # settings, urls, celery
│   ├── .env                # секреты (локально)
│   └── manage.py
├── package.json
└── SETUP.md                # эта инструкция
```

Settings:

- `config.settings.dev` — локальная разработка (SQLite)
- `config.settings.server` — VPS (см. `DEPLOY.md`)
- `config.settings.prod` — production (SQLite + Waitress, без Docker)
