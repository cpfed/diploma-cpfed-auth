#!/bin/bash
echo "--> Starting migrations"
python manage.py migrate
python manage.py reset_contest_schedules

echo "--> Starting gunicorn"
gunicorn cpfed.wsgi:application -b 0.0.0.0:8000 --log-level debug