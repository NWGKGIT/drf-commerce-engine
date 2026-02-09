import dj_database_url
from .base import *
import os

DEBUG = False

SECRET_KEY = env("SECRET_KEY")

# Database
DATABASES["default"] = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
    )

# --- Redis / Celery (Render Production) ---
REDIS_URL = env("REDIS_URL", default=None)
if REDIS_URL:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CACHES["default"]["LOCATION"] = REDIS_URL

# Allowed Hosts - Allow Render domains and specific domains
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])


RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    host_url = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if host_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(host_url)
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static Files / Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Strict CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True


# Email Service (e.g., SendGrid/AWS SES)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = env("EMAIL_HOST")
# ... will implement later

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" #temporary fix to 500 error post_save signal