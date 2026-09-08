import os
from pathlib import Path

from celery import Celery

# Load backend/.env before Django settings are imported
try:
    import environ

    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        environ.Env.read_env(str(env_file))
except Exception:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.server")

app = Celery("qalajob")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
