#!/usr/bin/env bash
set -o errexit

# celery -A config worker --beat -l info --concurrency=2 --pidfile= &

gunicorn config.wsgi:application