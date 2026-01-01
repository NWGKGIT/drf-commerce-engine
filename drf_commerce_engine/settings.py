from pathlib import Path
import os
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
DEBUG = env.bool("DEBUG", default=True)

INITIAL_ADMIN_TOKEN = env(
    "INITIAL_ADMIN_TOKEN",
    default="your-default-key",  # don't add a default key (insecure)
)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "server",
    ".ngrok-free.app",
    ".ngrok-free.dev",
]  # you can use environment variables here
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Created Apps
    "accounts.apps.AccountsConfig",
    "cart.apps.CartConfig",
    "orders.apps.OrdersConfig",
    "payments.apps.PaymentsConfig",
    "products.apps.ProductsConfig",
    "reviews.apps.ReviewsConfig",
    "wishlist.apps.WishlistConfig",
    "inventory.apps.InventoryConfig",
    "core.apps.CoreConfig",
    # Third Party
    "rest_framework",
    "rest_framework.authtoken",  # Required by dj-rest-auth even if using session
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
    "allauth.account.middleware.AccountMiddleware",  # REQUIRED by allauth
]

ROOT_URLCONF = "drf_commerce_engine.urls"

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

WSGI_APPLICATION = "drf_commerce_engine.wsgi.application"

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

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"  # for email verification
)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

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
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_CONFIRM_EMAIL_ON_GET = True  # Set True for easier development, False for Prod security
ACCOUNT_SIGNUP_FIELDS = {
    "email*": {"required": True},
    "first_name": {"required": False},
    "last_name": {"required": False},
}

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

REST_AUTH = {
    "USE_JWT": False,  # Explicitly set false if using sessions
    "SESSION_LOGIN": True,
    "REGISTER_SERIALIZER": "accounts.serializers.CustomRegisterSerializer",
    "USER_DETAILS_SERIALIZER": "accounts.serializers.UserDetailsSerializer",
    "LOGIN_SERIALIZER": "accounts.serializers.CustomLoginSerializer",
    # "LOGIN_ON_EMAIL_CONFIRMATION": True,  # Default is usually fine unless you need custom logic
}

ACCOUNT_AUTHENTICATED_REDIRECT_URL = "/api/"

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# --- Email ---
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# --- Spectacular ---
SPECTACULAR_SETTINGS = {
    "TITLE": "E-Commerce API",
    "DESCRIPTION": "The complete RESTful API for my E-commerce platform.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# --- Celery Configuration ---
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default="amqp://guest:guest@localhost:5672//"
)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE  # Uses 'UTC' from your existing settings

# --- Celery Beat Schedule ---
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "clear-expired-reservations-every-5-minutes": {
        "task": "inventory.tasks.clear_expired_reservations",
        # Run every 5 minutes. Adjust as needed.
        "schedule": crontab(minute="*/5"),
    },
    "cancel-unpaid-orders-every-10-mins": {
        "task": "inventory.tasks.cancel_unpaid_orders",
        "schedule": 600.0,  # 10 minutes
    },
}

# --- Chapa Config ---
CHAPA_SECRET_KEY = env("CHAPA_SECRET_KEY", default=None)
CHAPA_TRANSACTION_MODEL = "payments.Payment"
CHAPA_WEBHOOK_SECRET = env("CHAPA_WEBHOOK_SECRET", default="placeholder-for-build")
BACKEND_URL = env("BACKEND_URL", default=None)

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
