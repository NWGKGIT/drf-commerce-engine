from pathlib import Path
import os
import environ
import dj_database_url
from datetime import timedelta
from celery.schedules import crontab

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# config/settings.py -> config -> root
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env from the root directory
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

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
    'rest_framework_simplejwt.token_blacklist',
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

# Database
# Configured to use DATABASE_URL if present (Render), otherwise falls back to local vars
DATABASES = {
    "default": dj_database_url.config(
        default=f"postgres://{env('POSTGRES_USER', default='db_user')}:{env('POSTGRES_PASSWORD', default='default_password')}@{env('POSTGRES_HOST', default='localhost')}:{env('POSTGRES_PORT', default='5432')}/{env('POSTGRES_DB', default='db_table')}",
        conn_max_age=600
    )
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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
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
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access-token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh-token",
    "JWT_AUTH_HTTPONLY": True,
    "SESSION_LOGIN": False,
    "REGISTER_SERIALIZER": "apps.accounts.serializers.CustomRegisterSerializer",
    "USER_DETAILS_SERIALIZER": "apps.accounts.serializers.UserDetailsSerializer",
    "LOGIN_SERIALIZER": "apps.accounts.serializers.CustomLoginSerializer",
    "LOGIN_ON_EMAIL_CONFIRMATION": True,
}

# --- JWT CONFIG ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,  
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --- Spectacular ---
SPECTACULAR_SETTINGS = {
    "TITLE": "E-Commerce API",
    "DESCRIPTION": "The complete RESTful API for my E-commerce platform.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPS": ["apps.accounts", "apps.products", "apps.orders", "apps.inventory", "apps.reviews", "apps.wishlist"],
    "COMPONENT_SPLIT_PATCH": True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    "SECURITY": [
        {"jwtAuth": []},
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "jwtAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Token-based authentication with JWT",
            }
        }
    },
    "ENUM_NAME_OVERRIDES": {
        "PaymentStatusEnum": "apps.payments.models.Payment.PaymentStatus",
        "OrderStatusEnum": "apps.orders.models.OrderStatus",
    },
}

# --- Celery ---
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/2"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# --- Chapa ---
CHAPA_SECRET_KEY = env("CHAPA_SECRET_KEY", default=None)
CHAPA_WEBHOOK_SECRET = env("CHAPA_WEBHOOK_SECRET", default="placeholder-for-build")
BACKEND_URL = env("BACKEND_URL", default=None)
INITIAL_ADMIN_TOKEN = env("INITIAL_ADMIN_TOKEN", default=None)

# --- Security Settings (Applied in Production) ---
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
