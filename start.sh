#!/bin/bash

# 1. Start Nginx in the background
echo "Starting Nginx..."
nginx -c /app/nginx.conf.erb &

# 2. Start Gunicorn for App 1 (Flask + HTML) on port 8001 in the background
echo "Starting Gunicorn for App 1..."
cd Flask_app1 && gunicorn --bind 0.0.0.0:8001 --workers 2 manage:app &

# 3. Start Gunicorn for App 2 (Flask API) on port 8002 in the FOREGROUND
echo "Starting Gunicorn for App 2..."
cd ../Flask_app2 && gunicorn --bind 0.0.0.0:8002 --workers 2 run:app