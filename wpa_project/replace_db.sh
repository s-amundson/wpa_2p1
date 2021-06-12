#!/bin/bash

rm db.sqlite3
rm ./student_app/migrations/0*

python manage.py makemigrations
python manage.py migrate

python manage.py loaddata student_app/fixtures/f1.json