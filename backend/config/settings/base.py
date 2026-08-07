"""
QalaJob AI — Base Django Settings
Shared between dev and prod. Never use directly.
"""

import os
from pathlib import Path
from datetime import timedelta

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'), overwrite=True)

SECRET_KEY = env('SECRET_KEY', default='dev-secret-key-change-in-production')

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

AUTH_USER_MODEL = 'auth.User'

# ── Installed Apps ──────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_extensions',
    'django_filters',

    # Project apps
    'apps.users',
    'apps.profiles',
    'apps.companies',
    'apps.vacancies',
    'apps.applications',
    'apps.subscriptions',
    'apps.payments',
    'apps.resumes',
    'apps.saved_jobs',
    'apps.ai',
    'apps.admin_api',
    'apps.notifications',
    'apps.messaging',
    'apps.analytics',
    'apps.audit',
]

# ── Middleware ───────────────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.users.middleware.RequestLoggingMiddleware',
    'apps.users.middleware.BannedUserMiddleware',
    'apps.users.middleware.SecurityHeadersMiddleware',
    'apps.users.middleware.JSONPayloadSizeMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Database ────────────────────────────────────────────────────────

DB_ENGINE = env('DB_ENGINE', default='django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': env('DB_NAME', default='qalajob'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default='postgres'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }

# ── Auth Password Validators ───────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── i18n ────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = env('TIME_ZONE', default='Asia/Qyzylorda')
USE_I18N = True
USE_TZ = True

# ── Static / Media ─────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── REST Framework ──────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '120/minute',
        'auth': '10/minute',
        'ai': '30/hour',
    },
    'EXCEPTION_HANDLER': 'apps.users.exceptions.custom_exception_handler',
}

# ── Simple JWT ──────────────────────────────────────────────────────

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
}

# ── CORS ────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = env(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'accept-language',
]

# ── Celery ──────────────────────────────────────────────────────────

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ── Email ───────────────────────────────────────────────────────────

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='QalaJob AI <noreply@qalajob.kz>')

FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:3000')

# ── Payment Providers ──────────────────────────────────────────────

STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# ── AI Services ────────────────────────────────────────────────────

OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4o-mini')
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')
AI_RATE_LIMIT_PER_HOUR = env.int('AI_RATE_LIMIT_PER_HOUR', default=100)

# HeadHunter API (https://dev.hh.ru)
HH_USER_AGENT = env('HH_USER_AGENT', default='QalaJobAI/1.0 (noreply@qalajob.kz)')
HH_APP_TOKEN = env('HH_APP_TOKEN', default='')
HH_AREA = env('HH_AREA', default='40')  # 40 = Kazakhstan
HH_USE_DEMO = env.bool('HH_USE_DEMO', default=False)

# ── Firebase ───────────────────────────────────────────────────────

FIREBASE_WEB_API_KEY = env('FIREBASE_WEB_API_KEY', default='')

# ── DRF Spectacular ────────────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    'TITLE': 'QalaJob AI API',
    'DESCRIPTION': 'AI-powered HR platform for students and employers',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ── Logging ─────────────────────────────────────────────────────────

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'qalajob.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Max file upload size: 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Allowed upload file types
ALLOWED_RESUME_EXTENSIONS = ['.pdf', '.doc', '.docx']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_RESUME_SIZE_MB = 5
MAX_IMAGE_SIZE_MB = 2

# ── Media ────────────────────────────────────────────────────────────

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Frontend URL ────────────────────────────────────────────────────

FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:3000')
