#!/bin/sh

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

## Make migrations and migrate the database.
#echo "Making migrations and migrating the database. "
echo "Migrating the database"
#python manage.py makemigrations student_app payment program_app membership minutes --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
#python manage.py runapscheduler &

exec "$@"
