#!/bin/bash

echo "Running makemigrations"
python manage.py makemigrations

echo "Running migrations"
python manage.py migrate

echo "Running server"
gunicorn core.wsgi:application --bind 0.0.0.0:8000