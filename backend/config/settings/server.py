"""
QalaJob AI — VPS / bare-metal server settings
HTTP on Waitress (port 8088). SSL redirect is off unless USE_HTTPS=true.
SQLite by default; set DB_ENGINE=postgresql for Postgres.
"""

from .base import *  # noqa: F401,F403

DEBUG = env.bool("DEBUG", default=False)  # noqa: F405

# Do not force HTTPS when exposing Waitress on :8088 behind no reverse proxy
USE_HTTPS = env.bool("USE_HTTPS", default=False)  # noqa: F405
SECURE_SSL_REDIRECT = USE_HTTPS
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_HSTS_SECONDS = 31536000 if USE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS
SECURE_HSTS_PRELOAD = USE_HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if USE_HTTPS else None

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("CSRF_TRUSTED_ORIGINS", default="").split(",")  # noqa: F405
    if o.strip()
]

db_engine = env("DB_ENGINE", default="django.db.backends.sqlite3")  # noqa: F405

if "postgresql" in db_engine:
    DATABASES = {
        "default": {
            "ENGINE": db_engine,
            "NAME": env("DB_NAME"),  # noqa: F405
            "USER": env("DB_USER"),  # noqa: F405
            "PASSWORD": env("DB_PASSWORD"),  # noqa: F405
            "HOST": env("DB_HOST", default="localhost"),  # noqa: F405
            "PORT": env("DB_PORT", default="5432"),  # noqa: F405
            "CONN_MAX_AGE": 600,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# Optional Redis cache; otherwise local memory
if env("REDIS_URL", default=""):  # noqa: F405
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": env("REDIS_URL"),  # noqa: F405
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
