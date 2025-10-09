#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Change to Django project directory
cd WordGuesser

# Collect static files
python manage.py collectstatic --no-input

# Run migrations (if needed)
python manage.py migrate --no-input