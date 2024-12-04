#!/bin/bash
echo "--> Starting web process"
gunicorn cpfed.wsgi:application -b 0.0.0.0:8000