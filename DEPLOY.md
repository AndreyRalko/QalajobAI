# QalaJob AI — деплой в Production
#
# Без Docker. База: SQLite (backend/db.sqlite3).
# Backend: Waitress → порт 8088
# Frontend: Next.js → порт 3001

## Порты

| Сервис | Порт | Команда |
|--------|------|---------|
| Django API | `8088` | `python run_waitress.py` |
| Next.js | `3001` | `npm run start:prod` |

- Фронт: `http://YOUR_IP:3001`
- API health: `http://YOUR_IP:8088/api/health/`
- API v1: `http://YOUR_IP:8088/api/v1/`

Settings: `config.settings.prod` (или `config.settings.server` — тоже SQLite).

---

## 1. Подготовка сервера

Нужны: **Python 3.11+**, **Node.js 20+**, git. Docker и PostgreSQL не нужны.

```bash
git clone https://github.com/AndreyRalko/QalajobAI.git
cd QalajobAI
sudo ufw allow 3001/tcp
sudo ufw allow 8088/tcp
```

---

## 2. Backend (Waitress + SQLite)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p logs media staticfiles
cp .env.prod.example .env
nano .env
```

В `.env` обязательно:

```env
SECRET_KEY=длинный-случайный-ключ
DJANGO_SETTINGS_MODULE=config.settings.prod
ALLOWED_HOSTS=YOUR_IP,localhost
FRONTEND_URL=http://YOUR_IP:3001
CORS_ALLOWED_ORIGINS=http://YOUR_IP:3001
CSRF_TRUSTED_ORIGINS=http://YOUR_IP:3001
WAITRESS_PORT=8088
OPENAI_API_KEY=sk-...
USE_HTTPS=false
```

Миграции (создадут `db.sqlite3`):

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # опционально
```

Запуск:

```bash
python run_waitress.py
# или: bash ../scripts/start-backend.sh
```

Проверка: `curl http://127.0.0.1:8088/api/health/`

---

## 3. Frontend (Next.js :3001)

```bash
cd /path/to/QalajobAI
cp .env.production.example .env.production.local
nano .env.production.local
```

```env
NEXT_PUBLIC_API_URL=http://YOUR_IP:8088/api/v1
```

```bash
npm install
npm run build
npm run start:prod
# или: bash scripts/start-frontend.sh
```

Откройте: `http://YOUR_IP:3001`

> После смены `NEXT_PUBLIC_API_URL` снова выполните `npm run build`.

---

## 4. Windows Server (PowerShell)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.prod.example .env
# отредактируйте .env
New-Item -ItemType Directory -Force -Path logs, media, staticfiles | Out-Null
$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
python manage.py migrate
python manage.py collectstatic --noinput
python run_waitress.py
```

```powershell
cd ..
Copy-Item .env.production.example .env.production.local
# NEXT_PUBLIC_API_URL=http://YOUR_IP:8088/api/v1
npm install
npm run build
npm run start:prod
```

---

## 5. Держать процессы постоянно (Linux systemd)

```bash
sudo cp deploy/systemd/qalajob-api.service /etc/systemd/system/
sudo cp deploy/systemd/qalajob-web.service /etc/systemd/system/
sudo nano /etc/systemd/system/qalajob-api.service   # путь /opt/QalajobAI при необходимости
```

В unit API укажите:

```ini
Environment=DJANGO_SETTINGS_MODULE=config.settings.prod
EnvironmentFile=/opt/QalajobAI/backend/.env
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now qalajob-api qalajob-web
sudo systemctl status qalajob-api qalajob-web
```

Альтернатива: `pm2`, `screen`, `tmux`.

---

## 6. LMS sync

Туннель вручную, затем команда:

```bash
ssh -L 6080:localhost:6080 user@lms-host
cd backend && source venv/bin/activate
python manage.py sync_lms_daily
```

Celery/Redis нужны только если хотите автозапуск по расписанию.

---

## 7. Чеклист

1. Backend отвечает на `:8088/api/health/`
2. Frontend открывается на `:3001`
3. В Network запросы идут на `http://YOUR_IP:8088/api/v1/...`
4. CORS/CSRF совпадают с URL фронта
5. `SECRET_KEY` не дефолтный, `DEBUG=false`
6. Есть файл `backend/db.sqlite3` после `migrate`
7. `OPENAI_API_KEY` задан
8. Firewall пропускает `3001` и `8088`
9. Бэкап: копируйте `backend/db.sqlite3` и `backend/media/`

---

## Важно

- Docker **не используется**
- БД — **SQLite** (`backend/db.sqlite3`), PostgreSQL не нужен
- `backend/.env` и `.env.production.local` не коммитить
- Шаблоны: `backend/.env.prod.example`, `.env.production.example`
- Для HTTPS позже: nginx (`deploy/nginx/qalajob.conf`) и `USE_HTTPS=true`
