#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py create_db

echo "================================ Sever is starting now  =================================="
gunicorn --bind 0.0.0.0:8000 --reload wsgi:app



exec "$@"
