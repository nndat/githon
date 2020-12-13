#!/bin/sh
set -e

echo "Waiting for database..."
wait-for db:3306 -t 60 -- echo "Done"

echo "Applying migrations..."
python githon/manage.py migrate

echo "Collecting static files..."
python githon/manage.py collectstatic --noinput

echo "Creating superuser..."
cat <<EOF | python githon/manage.py shell
import os
from django.contrib.auth import get_user_model

User = get_user_model()  # get the currently active user model,

username = os.getenv('ADMIN_USERNAME', 'admin')
password = os.getenv('ADMIN_PASSWORD', 'Pas5w0rd')

User.objects.filter(username=username).exists() or \
    User.objects.create_superuser(username, password)
EOF

export GUNICORN_CMD_ARGS="--chdir githon --bind=:$APP_PORT --workers=$(($(nproc) + 1))"

exec "$@"