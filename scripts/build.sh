#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# First and one use only (Uncomment this line for the initial deployment to seed the DB, then comment it out again!)
# python manage.py seed_db --flush
