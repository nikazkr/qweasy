#!/bin/bash

echo "Running makemigrations"
python manage.py makemigrations

echo "Running migrations"
python manage.py migrate

echo "collecting static files"
python manage.py collectstatic --no-input

echo "Running server"
gunicorn core.wsgi:application --bind 0.0.0.0:8000

#python manage.py runserver 0.0.0.0:8000