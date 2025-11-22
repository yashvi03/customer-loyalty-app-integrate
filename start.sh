#!/bin/bash

# Create required nginx directories
mkdir -p /tmp/nginx/logs
mkdir -p /tmp/nginx/client_body_temp
mkdir -p /tmp/nginx/proxy_temp
mkdir -p /tmp/nginx/fastcgi_temp
mkdir -p /tmp/nginx/uwsgi_temp
mkdir -p /tmp/nginx/scgi_temp

# Process the nginx.conf.erb template to replace <%= ENV["PORT"] %>
erb nginx.conf.erb > /tmp/nginx.conf

# Start Nginx with the processed config
echo "Starting Nginx..."
nginx -c /tmp/nginx.conf &

# Start Gunicorn for Flask_app1
echo "Starting Gunicorn for App 1..."
python -m gunicorn --bind 0.0.0.0:8001 --workers 2 --chdir ./Flask_app1 app:app &

# Start Gunicorn for Flask_app2 (foreground - keeps dyno alive)
echo "Starting Gunicorn for App 2..."
python -m gunicorn --bind 0.0.0.0:8002 --workers 2 --chdir ./Flask_app2 run:app