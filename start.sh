#!/bin/bash
# This script starts the services for the combined app on Heroku.

# 1. Start Nginx in the background.
echo "Starting Nginx..."
nginx -c /app/nginx.conf.erb &

# 2. Start the Gunicorn server for the first Flask app in the background.
# We use --chdir to tell Gunicorn where the app is, instead of using 'cd'.
# We use 'python -m gunicorn' to ensure the command is found.
echo "Starting Gunicorn for App 1..."
python -m gunicorn --bind 0.0.0.0:8001 --workers 2 --chdir ./Flask_app1 app:app &

# 3. Start the Gunicorn server for the second Flask app in the FOREGROUND.
# This is the command that keeps the dyno alive.
echo "Starting Gunicorn for App 2..."
python -m gunicorn --bind 0.0.0.0:8002 --workers 2 --chdir ./Flask_app2 run:app