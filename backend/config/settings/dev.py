"""
QalaJob AI — Development Settings
"""

from .base import *  # noqa: F401,F403

DEBUG = True

# Dev-only: allow all hosts
ALLOWED_HOSTS = ['*']

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable rate limiting in dev
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []  # noqa: F405

# Relax CORS for dev
CORS_ALLOW_ALL_ORIGINS = True

# Use SQLite for quick local dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

# Shorter token lifetime in dev for testing refresh
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = __import__('datetime').timedelta(minutes=60)  # noqa: F405
