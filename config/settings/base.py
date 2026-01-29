from pathlib import Path
import os
import environ

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# config/settings/base.py -> config/settings -> config -> root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Read .env from the root directory
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY: Keep secret key here or override in prod
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Created Apps
    "apps.accounts.apps.AccountsConfig",
    "apps.cart.apps.CartConfig",
    "apps.orders.apps.OrdersConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.products.apps.ProductsConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.wishlist.apps.WishlistConfig",
    "apps.inventory.apps.InventoryConfig",
    "apps.core.apps.CoreConfig",
    # Third Party
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
    "drf_spectacular",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database - Default config (Can be overridden in env specific files)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="db_table"),
        "USER": env("POSTGRES_USER", default="db_user"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="default_password"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Authentication & Authorization ---
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# --- AllAuth Settings ---
SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_CONFIRM_EMAIL_ON_GET = True # Can override in Prod
ACCOUNT_SIGNUP_FIELDS = {
    "email*": {"required": True},
    "first_name": {"required": False},
    "last_name": {"required": False},
}
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/api/"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/api/"
ACCOUNT_AUTHENTICATED_REDIRECT_URL = "/api/"

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

REST_AUTH = {
    "USE_JWT": False,
    "SESSION_LOGIN": True,
    "REGISTER_SERIALIZER": "apps.accounts.serializers.CustomRegisterSerializer",
    "USER_DETAILS_SERIALIZER": "apps.accounts.serializers.UserDetailsSerializer",
    "LOGIN_SERIALIZER": "apps.accounts.serializers.CustomLoginSerializer",
    "LOGIN_ON_EMAIL_CONFIRMATION": True,
}

# --- Spectacular ---
SPECTACULAR_SETTINGS = {
    "TITLE": "E-Commerce API",
    "DESCRIPTION": "The complete RESTful API for my E-commerce platform.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPS": ["apps.accounts", "apps.products", "apps.orders", "apps.inventory", "apps.reviews", "apps.wishlist"],
}

# --- Celery ---
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    "clear-expired-reservations-every-5-minutes": {
        "task": "inventory.tasks.clear_expired_reservations",
        "schedule": crontab(minute="*/5"),
    },
    "cancel-unpaid-orders-every-10-mins": {
        "task": "inventory.tasks.cancel_unpaid_orders",
        "schedule": 600.0,
    },
}

# --- Chapa ---
CHAPA_SECRET_KEY = env("CHAPA_SECRET_KEY", default=None)
CHAPA_WEBHOOK_SECRET = env("CHAPA_WEBHOOK_SECRET", default="placeholder-for-build")
BACKEND_URL = env("BACKEND_URL", default=None)