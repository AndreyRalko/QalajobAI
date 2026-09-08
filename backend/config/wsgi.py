import os

from django.core.wsgi import get_wsgi_application

# WSGI defaults to server settings (not DEBUG/dev).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.server")

application = get_wsgi_application()
