#!/bin/sh
set -e

echo "Waiting for database..."
wait-for db:3306 -t 60 -- echo "Done"

echo "Applying migrations..."
python githon/manage.py migrate

echo "Collecting static files..."
python githon/manage.py collectstatic --noinput

echo "Creating superuser..."
{
    python githon/manage.py createsuperuser --noinput
} || {
    echo "That username is already taken"
}

export GUNICORN_CMD_ARGS="--chdir githon --bind=:$APP_PORT --workers=$(($(nproc) + 1))"

exec "$@"