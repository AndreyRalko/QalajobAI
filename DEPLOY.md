# QalaJob AI — деплой (Django monolith)
#
# Без Docker. База: SQLite (backend/db.sqlite3).
# Один процесс: Waitress → порт 8088 (UI + API)

## Порты

| Сервис | Порт | Команда |
|--------|------|---------|
| Django (UI + API) | `8088` | `python run_waitress.py` |

- Сайт: `http://YOUR_IP:8088`
- Вход: `http://YOUR_IP:8088/login/`
- API health: `http://YOUR_IP:8088/api/health/`
- API v1: `http://YOUR_IP:8088/api/v1/`
- Django Admin: `http://YOUR_IP:8088/admin/`

Settings: `config.settings.server` или `config.settings.prod`.

---

## 1. Подготовка сервера

Нужны: **Python 3.11+**, git. Node.js / Next.js **не нужны**.

```bash
git clone https://github.com/AndreyRalko/QalajobAI.git
cd QalajobAI
sudo ufw allow 8088/tcp
```

---

## 2. Backend + UI (Waitress + SQLite)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.server.example .env       # или .env.prod.example
# Обязательно смените SECRET_KEY
mkdir -p logs
python manage.py migrate
python manage.py collectstatic --noinput
python run_waitress.py
```

Проверка: `curl http://127.0.0.1:8088/api/health/` и открыть `http://YOUR_IP:8088`.

### Важные env

```env
DJANGO_SETTINGS_MODULE=config.settings.server
SECRET_KEY=...strong...
ALLOWED_HOSTS=YOUR_IP,localhost,127.0.0.1
FRONTEND_URL=http://YOUR_IP:8088
CSRF_TRUSTED_ORIGINS=http://YOUR_IP:8088
CORS_ALLOWED_ORIGINS=http://YOUR_IP:8088
WAITRESS_PORT=8088
```

На Windows локально: двойной клик **`start.bat`**.

---

## 3. systemd (Linux)

Пример unit (пути поправьте под сервер):

```ini
[Unit]
Description=QalaJob AI
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

---

## 4. Чеклист

1. Сайт открывается на `:8088`
2. Логин Platonus работает (`/login/`)
3. Кабинет студента: `/app/student/ai/resume/`
4. Админка продукта: `/app/admin/`
5. API health отвечает
6. Firewall пропускает `8088`
