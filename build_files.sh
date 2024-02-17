#!/usr/bin/env bash

echo "Building project packages..."
python3 -m pip install -r requirements.txt

echo "Migration databases..."
python3 manage.py makemigrations --no-input --clear
python3 manage.py migrate --no-input --clear

echo "Collecting static files..."
python3 manage.py collectstatic --no-input --clear