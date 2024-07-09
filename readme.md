# Website for Woodley Park Archers
This project uses docker containers. The site is built on the Django web framework. 
It uses Postgres, Celery, RabbitMQ, Nginx

### To setup development environment:
Create 'wpa_project/wpa_project/secrets.json' using keys from privatefiles.txt\
Create 'wpa_project/wpa_project.env' using keys from privatefiles.txt
Run this command: docker exec -it django_dev python manage.py migrate

### To run navigate to the docker_development folder: 
Note sudo may be needed. Also, docker-compose has been replaced docker compose\
&nbsp;&nbsp; docker compose build \
&nbsp;&nbsp; docker compose up

### To run tests:
docker exec -it django_dev python manage.py test [app]\
To isolate one test from other tests uncomment the @tag('temp') above the test then run: \
docker exec -it django_dev python manage.py test --tag temp

### To load fixture data into database
Use this to import the fixture data for manual testing.\
docker exec -it django_dev python manage.py loaddata beginner_schedule.json f1.json