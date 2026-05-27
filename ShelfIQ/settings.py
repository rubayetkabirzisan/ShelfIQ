import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security — NEVER commit the real secret key to git
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# Debug mode — True in development, False in production
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ─────────────────────────────────────────
# Installed apps
# Django needs to know about every app and package you're using
# ─────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party packages
    'rest_framework',           # Django REST Framework
    'rest_framework_simplejwt', # JWT auth
    'corsheaders',              # CORS for Next.js frontend

    # Our apps (we'll add these as we create them)
    'accounts',
]

# ─────────────────────────────────────────
# Middleware — these run on every request, in order
# ─────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ShelfIQ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ShelfIQ.wsgi.application'

# ─────────────────────────────────────────
# Database — SQLite for now, zero config needed
# ─────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─────────────────────────────────────────
# Custom user model — we'll build this in the accounts app
# ─────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

# ─────────────────────────────────────────
# Django REST Framework config
# ─────────────────────────────────────────
REST_FRAMEWORK = {
    # All endpoints require JWT authentication by default
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # All endpoints require login by default
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# ─────────────────────────────────────────
# JWT settings
# ─────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ─────────────────────────────────────────
# CORS — allow Next.js frontend to call this API
# ─────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True

# ─────────────────────────────────────────
# Media files — uploaded shelf images
# ─────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files
STATIC_URL = 'static/'

# Password validation (keep defaults)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────
# External API keys — read from .env
# ─────────────────────────────────────────
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
TWILIO_WHATSAPP_TO = os.environ.get('TWILIO_WHATSAPP_TO', '')