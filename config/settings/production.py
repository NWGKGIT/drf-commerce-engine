import dj_database_url
from .base import *

DEBUG = False

SECRET_KEY = env("SECRET_KEY")

# Allowed Hosts - Allow Render domains and specific domains
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Database
# Render provides DATABASE_URL in environment
DATABASES["default"] = dj_database_url.config(conn_max_age=600)

# Static Files - Whitenoise
# Ensure STATIC_ROOT is set in base.py (it is)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Strict CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Email Service (e.g., SendGrid/AWS SES)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = env("EMAIL_HOST")
# ... implement later

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'