#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

if [[ ! -d venv ]]; then
  echo "Create venv first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate

mkdir -p logs media staticfiles
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec python run_waitress.py
