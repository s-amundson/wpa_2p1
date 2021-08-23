#!/bin/bash

cd "$(dirname "$0")"

rm db.sqlite3
rm ../wpa_project/student_app/migrations/0*
rm ../wpa_project/payment/migrations/0*
rm ../wpa_project/membership/migrations/0*
rm -R ../wpa_project/student_app/media/signatures

docker exec -it \django_dev python manage.py makemigrations student_app
docker exec -it \django_dev python manage.py makemigrations payment
docker exec -it \django_dev python manage.py makemigrations membership

docker exec -it \django_dev python manage.py migrate

docker exec -it \django_dev python manage.py loaddata student_app/fixtures/f1.json