#!/bin/bash
echo "--> Starting migrations"
python manage.py migrate

echo "--> Starting gunicorn"
gunicorn cpfed.wsgi:application -b 0.0.0.0:8000