#!/bin/bash

rm wpa_project/db.sqlite3
rm ./student_app/migrations/0*

python manage.py makemigrations student_app
python manage.py migrate

python manage.py loaddata student_app/fixtures/f1.json