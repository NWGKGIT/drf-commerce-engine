#!/bin/sh

if [ "$DATABASE" = "postgres" ] || [ -n "$POSTGRES_HOST" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
uv run python manage.py migrate

exec "$@"
