"""
QalaJob AI — Production Settings (Waitress + SQLite, no Docker)
"""

from .base import *  # noqa: F401,F403

DEBUG = False

if SECRET_KEY == "dev-secret-key-change-in-production":  # noqa: F405
    raise RuntimeError(
        "Refusing to start with the default SECRET_KEY. "
        "Set a strong SECRET_KEY in backend/.env"
    )

if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["localhost", "127.0.0.1"]:  # noqa: F405
    raise RuntimeError(
        "Set ALLOWED_HOSTS to your server IP or domain before using production settings."
    )

# HTTPS only when behind a reverse proxy / TLS terminator
USE_HTTPS = env.bool("USE_HTTPS", default=False)  # noqa: F405
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=USE_HTTPS)  # noqa: F405
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_HSTS_SECONDS = 31536000 if USE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS
SECURE_HSTS_PRELOAD = USE_HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if USE_HTTPS else None
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("CSRF_TRUSTED_ORIGINS", default="").split(",")  # noqa: F405
    if o.strip()
]
if not CSRF_TRUSTED_ORIGINS:
    raise RuntimeError(
        "Set CSRF_TRUSTED_ORIGINS to your frontend origin(s), "
        "e.g. http://YOUR_IP:3001 or https://qalajob.example.com"
    )

# Drop local-only tooling in production
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django_extensions"]  # noqa: F405

# SQLite (no PostgreSQL / no Docker)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        "OPTIONS": {
            "timeout": 30,
        },
    }
}

# Optional Redis; otherwise in-process cache
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

EMAIL_BACKEND = env(  # noqa: F405
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ENABLE_API_DOCS = env.bool("ENABLE_API_DOCS", default=False)  # noqa: F405

LOGGING["handlers"]["file"]["level"] = "WARNING"  # noqa: F405
LOGGING["handlers"]["console"]["level"] = "INFO"  # noqa: F405

SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(env("SENTRY_TRACES_SAMPLE_RATE", default="0.1")),  # noqa: F405
        send_default_pii=False,
        environment=env("SENTRY_ENVIRONMENT", default="production"),  # noqa: F405
    )
