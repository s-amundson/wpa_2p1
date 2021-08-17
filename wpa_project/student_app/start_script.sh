#!/bin/sh

gunicorn wpa_project.wsgi:application --bind 0.0.0.0:8000 --workers=4
python manage.py runapscheduler &

exec "$@"
