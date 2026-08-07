# QalaJob AI — деплой на сервер
#
# Backend: Waitress WSGI → порт **8088**
# Frontend: Next.js → порт **3001**

## Порты

| Сервис | Порт | Команда |
|--------|------|---------|
| Django API | `8088` | `python run_waitress.py` |
| Next.js | `3001` | `npm run start:prod` |

Пример URL (замените IP):

- Фронт: `http://YOUR_IP:3001`
- API health: `http://YOUR_IP:8088/api/health/`
- API v1: `http://YOUR_IP:8088/api/v1/`

---

## 1. Подготовка сервера

Нужны: **Python 3.11+**, **Node.js 20+**, git.

Откройте порты в firewall:

```bash
# Ubuntu ufw (пример)
sudo ufw allow 3001/tcp
sudo ufw allow 8088/tcp
```

Клонируйте репозиторий:

```bash
git clone https://github.com/AndreyRalko/QalajobAI.git
cd QalajobAI
```

---

## 2. Backend (Waitress :8088)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p logs
cp .env.server.example .env
# Отредактируйте .env — SECRET_KEY, ALLOWED_HOSTS, CORS, OPENAI_API_KEY
nano .env
```

В `.env` обязательно:

```env
SECRET_KEY=длинный-случайный-ключ
DJANGO_SETTINGS_MODULE=config.settings.server
ALLOWED_HOSTS=YOUR_IP,localhost
FRONTEND_URL=http://YOUR_IP:3001
CORS_ALLOWED_ORIGINS=http://YOUR_IP:3001
CSRF_TRUSTED_ORIGINS=http://YOUR_IP:3001
OPENAI_API_KEY=sk-...
WAITRESS_PORT=8088
```

Миграции и статика:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # опционально
```

Запуск:

```bash
python run_waitress.py
# или из корня репозитория:
# bash scripts/start-backend.sh
```

Проверка: `curl http://127.0.0.1:8088/api/health/`

---

## 3. Frontend (Next.js :3001)

В **корне** репозитория (новый терминал):

```bash
cd /path/to/QalajobAI
cp .env.production.example .env.production.local
# Укажите API бэкенда — URL вшивается при build!
nano .env.production.local
```

```env
NEXT_PUBLIC_API_URL=http://YOUR_IP:8088/api/v1
```

Сборка и запуск:

```bash
npm install
npm run build
npm run start:prod
# или: bash scripts/start-frontend.sh
```

Откройте: `http://YOUR_IP:3001`

> После смены `NEXT_PUBLIC_API_URL` нужно снова сделать `npm run build`.

---

## 4. Windows Server (PowerShell)

**Backend**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.server.example .env
# отредактируйте .env
New-Item -ItemType Directory -Force -Path logs | Out-Null
$env:DJANGO_SETTINGS_MODULE = "config.settings.server"
python manage.py migrate
python manage.py collectstatic --noinput
python run_waitress.py
```

**Frontend**

```powershell
cd ..
Copy-Item .env.production.example .env.production.local
# отредактируйте NEXT_PUBLIC_API_URL
npm install
npm run build
npm run start:prod
```

---

## 5. Держать процессы постоянно (Linux)

Пример **systemd** для бэкенда `/etc/systemd/system/qalajob-api.service`:

```ini
[Unit]
Description=QalaJob AI Waitress
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/QalajobAI/backend
Environment=DJANGO_SETTINGS_MODULE=config.settings.server
EnvironmentFile=/opt/QalajobAI/backend/.env
ExecStart=/opt/QalajobAI/backend/venv/bin/python run_waitress.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Frontend `/etc/systemd/system/qalajob-web.service`:

```ini
[Unit]
Description=QalaJob AI Next.js
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/QalajobAI
Environment=HOSTNAME=0.0.0.0
Environment=PORT=3001
ExecStart=/usr/bin/npm run start:prod
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now qalajob-api qalajob-web
```

Альтернатива: `pm2`, `screen`, `tmux`.

---

## 6. Чеклист

1. Backend отвечает на `:8088/api/health/`
2. Frontend открывается на `:3001`
3. В браузере Network → запросы идут на `http://YOUR_IP:8088/api/v1/...`
4. CORS не блокирует (origins совпадают с URL фронта)
5. `OPENAI_API_KEY` задан на сервере
6. Firewall пропускает `3001` и `8088`

---

## Важно

- `backend/.env` и `.env.production.local` **не коммитить** (секреты).
- Settings: `config.settings.server` — HTTP, SQLite по умолчанию, Waitress.
- Для HTTPS + домена позже: nginx как reverse proxy и `USE_HTTPS=true`.
