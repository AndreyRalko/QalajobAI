#!/usr/bin/env bash
# Start backend (Waitress :8088) — run from repo root or backend/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
elif [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

mkdir -p logs
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.server}"

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec python run_waitress.py
