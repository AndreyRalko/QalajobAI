"""
Run Django with Waitress on 0.0.0.0:8088

Usage (from backend/ with venv activated):
  python run_waitress.py
"""

from __future__ import annotations

import os
from pathlib import Path

# Load backend/.env before Django settings are imported
try:
    import environ

    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        environ.Env.read_env(str(env_file))
except Exception:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.server")

from waitress import serve  # noqa: E402
from config.wsgi import application  # noqa: E402

HOST = os.environ.get("WAITRESS_HOST", "0.0.0.0")
PORT = int(os.environ.get("WAITRESS_PORT", "8088"))
THREADS = int(os.environ.get("WAITRESS_THREADS", "8"))

if __name__ == "__main__":
    print(
        f"Waitress serving {os.environ['DJANGO_SETTINGS_MODULE']} "
        f"on http://{HOST}:{PORT} (threads={THREADS})"
    )
    serve(application, host=HOST, port=PORT, threads=THREADS)
