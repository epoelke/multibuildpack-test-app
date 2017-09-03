#!/bin/sh
set -ex
$APP_ROOT/start_logging.sh
uwsgi --master --processes 4 --threads 2 --http /tmp/uwsgi.sock --wsgi-file public/app.py &
nginx -p $APP_ROOT/nginx -c $APP_ROOT/nginx/conf/nginx.conf
