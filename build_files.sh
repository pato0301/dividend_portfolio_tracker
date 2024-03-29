#!/usr/bin/env bash

# Exit on error
set -o errexit

echo "Building project packages..."
pip install -r requirements.txt

echo "Migration databases..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput