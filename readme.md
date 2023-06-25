# Website for Woodley Park Archers
This project uses docker containers. The site is built on the Django web framework. 
It uses Postgres, Celery, RabbitMQ, Nginx

### To setup development enviroment:
Create 'wpa_project/wpa_project/secrets.json' using keys from privatefiles.txt\
Create 'wpa_project/wpa_project.env' using keys from privatefiles.txt

### To run navigate to the docker_development folder:
&nbsp;&nbsp; docker-compose build \
&nbsp;&nbsp; docker-compose up

### To run tests:
docker exec -it django_dev python manage.py test