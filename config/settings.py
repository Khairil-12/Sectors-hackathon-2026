import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

load_dotenv(BASE_DIR / ".env")

# Validate required environment variables
if not os.getenv("GROQ_API_KEY"):
    raise ImproperlyConfigured(
        "GROQ_API_KEY environment variable not set. "
        "Create a .env file based on .env.template and add your Groq API key."
    )
if not os.getenv("SECTORS_API_KEY"):
    raise ImproperlyConfigured(
        "SECTORS_API_KEY environment variable not set. "
        "Create a .env file based on .env.template and add your Sectors Financial API key."
    )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key secret in production!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-do-not-use-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_browser_reload",
]

LOCAL_APPS = [
    "research",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#password-validators
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-primary-key-field-type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACK = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django Cache (local memory, Redis, or DB)
CACHE_BACKEND = os.getenv("DJANGO_CACHE_BACKEND", "localmemory")
CACHES = {
    "default": {
        "BACKEND": {
            "localmemory": "django.core.cache.backends.locmem.LocMemCache",
            "redis": "django_redis.cache.RedisCache",
            "db": "django.core.cache.backends.db.DatabaseCache",
        }.get(CACHE_BACKEND, "django.core.cache.backends.locmem.LocMemCache"),
        "LOCATION": os.getenv("DJANGO_CACHE_LOCATION", "unique-cache"),
        "TIMEOUT": int(os.getenv("DJANGO_CACHE_TIMEOUT", "300")),
    }
}

# Groq Cloud Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Sectors Financial API Configuration
SECTORS_API_KEY = os.getenv("SECTORS_API_KEY", "")
SECTORS_BASE_URL = "https://api.sectors.app"
