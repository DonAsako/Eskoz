#!/bin/sh

echo "Migration application..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Compiling translation messages..."
python manage.py compilemessages

echo "Launch of Gunicorn..."
exec gunicorn eskoz.wsgi:application --bind 0.0.0.0:8000
