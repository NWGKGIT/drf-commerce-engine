# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.0
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHON_BUFFERED=1

WORKDIR /app

# Install system dependencies for PostgreSQL and building packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files (needed for DRF/Admin UI)
RUN python manage.py collectstatic --noinput

# Security: Run as non-privileged user
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" --no-create-home --uid "${UID}" appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default command (Production ready)
CMD ["gunicorn", "backend_ecommerce.wsgi:application", "--bind", "0.0.0.0:8000"]