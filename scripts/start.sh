#!/usr/bin/env bash
set -o errexit

export PATH="$HOME/.local/bin:$PATH"

# celery -A config worker --beat -l info --concurrency=2 --pidfile= &

uv run gunicorn config.wsgi:application
