# QalaJob AI — инструкция по запуску

**Django monolith**: UI + API на одном процессе Waitress (`:8088`).

| Сервис | URL |
|--------|-----|
| Сайт / кабинет | http://localhost:8088 |
| API | http://localhost:8088/api/v1/ |
| Health | http://localhost:8088/api/health/ |
| Django Admin | http://localhost:8088/admin/ |
| Ollama (опционально) | http://127.0.0.1:11434 |

---

## 1. Что установить

| Компонент | Зачем |
|-----------|--------|
| **Python** 3.11+ | бэкенд + UI |
| **Ollama** (опционально) | локальная LLM |
| **Redis** (опционально) | Celery / LMS sync по расписанию |

Node.js / Next.js **не нужны**.

---

## 2. Первый запуск

```powershell
cd D:\projects\QalajobAI\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# настройте backend\.env (SECRET_KEY, OPENAI_*, LLM_*, LMS_*)
python manage.py migrate
python manage.py collectstatic --noinput
python run_waitress.py
```

Или двойной клик **`start.bat`** в корне.

Тестовый студент: `Иванов_Иван` / `Student123`  
Админ: `Сидоров_Админ` / `Admin1234`

---

## 3. AI (гибрид)

В `backend\.env`:

- `LLM_HYBRID_ENABLED=true`
- локально: Ollama (`LLM_LOCAL_MODEL`, по умолчанию `gemma3:4b`)
- облако: `OPENAI_API_KEY` + fallback при сбое локальной модели

Подробнее про деплой: **[DEPLOY.md](./DEPLOY.md)**.
