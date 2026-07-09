#!/usr/bin/env bash
# Exit on error
set -o errexit

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv sync --locked --no-dev --no-install-project

uv run python manage.py collectstatic --no-input

uv run python manage.py migrate

# First and one use only (Uncomment this line for the initial deployment to seed the DB, then comment it out again!)
# uv run python manage.py seed_db --flush
