from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "server",
    ".ngrok-free.app",
    ".ngrok-free.dev",
]

# Development CORS/CSRF
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["https://*.ngrok-free.app"]

# Print emails to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"