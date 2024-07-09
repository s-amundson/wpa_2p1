# Website for Woodley Park Archers
This project uses docker containers. The site is built on the Django web framework. 
It uses Postgres, Celery, RabbitMQ, Nginx

### To setup development environment:
1. Create 'wpa_project/wpa_project/secrets.json' using keys from *privatefiles.txt*
1. Create 'wpa_project/wpa_project.env' using keys from *privatefiles.txt*
    * **Optional:** Change the value of "SESSION_COOKIE_AGE" to 86400 to avoid being logged out too soon
1. Run this command to migrate the database: `docker exec -it django_dev python manage.py migrate`

**Note:** Ask Sam for the credentials for "SQUARE_CONFIG" and "RECAPTCHA".

### To load fixture data into database:
Use this to import the fixture data for manual testing.\
`docker exec -it django_dev python manage.py loaddata beginner_schedule.json f1.json`

**Note:** The *f1.json* file contains users you may log in as. User 1 is a superuser, User 2 is an instructor, and Users 3-5 are regular members. Ask Sam for the password for these users. You may also create your own user to log in with.

### To run the app, navigate to the docker_development folder: 
Run the following commands. **Note:** `sudo` may be needed. Also, `docker-compose` has been replaced with `docker compose`
1. &nbsp;&nbsp; `docker compose build`
2. &nbsp;&nbsp; `docker compose up`

If the above ran successfully, open your browser and visit https://0.0.0.0:8000/ to access the dev version of the website.

### To run tests:
`docker exec -it django_dev python manage.py test [app]`\

To isolate one test from other tests uncomment the @tag('temp') above the test then run: 

`docker exec -it django_dev python manage.py test --tag temp`
