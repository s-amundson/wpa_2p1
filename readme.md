# Website for Woodley Park Archers
This project uses [Docker](https://www.docker.com/) containers. The site is built on the [Django web framework](https://www.djangoproject.com/). It also uses the following frameworks. These are loaded up in the Docker container and do not need to be manually installed:

1. [PostgreSQL](https://www.postgresql.org/)
1. [Celery](https://docs.celeryq.dev/en/stable/)
1. [RabbitMQ](https://www.rabbitmq.com/)
1. [Nginx](https://github.com/nginx/nginx/)

## To setup development environment:
1. Clone this repo
1. Create 'wpa_project/wpa_project/secrets.json' using keys from *privatefiles.txt*
1. Create 'wpa_project/wpa_project.env' using keys from *privatefiles.txt*
    * **Optional:** Change the value of "SESSION_COOKIE_AGE" to 86400 to avoid being logged out too soon
1. Run this command to migrate the database: `docker exec -it django_dev python manage.py migrate`

**Note:** Ask Sam for the credentials for "SQUARE_CONFIG" and "RECAPTCHA".

## To load fixture data into database:
Use this to import the fixture data for manual testing.\
`docker exec -it django_dev python manage.py loaddata beginner_schedule.json 
f1.json level.json pinscores.json policy_article.json`

**Note:** The *f1.json* file contains users you may log in as. User 1 is a superuser, User 2 is an instructor, and Users 3-5 are regular members. Ask Sam for the password for these users. You may also create your own user to log in with.

## To run the app:
1. Navigate to the 'docker_development' folder.
1. Run the following commands. **Note:** `sudo` may be needed. Also, `docker-compose` has been replaced with `docker compose`
    1. &nbsp;&nbsp; `docker compose build`
    1. &nbsp;&nbsp; `docker compose up`

If the above ran successfully, open your browser and visit https://0.0.0.0:8000/ to access the dev version of the website.

To view the site on other devices on your network, add the IP address of the host machine to the "ALLOWED_HOSTS" in secrets.json.

## To run tests:
`docker exec -it django_dev python manage.py test [app]`

To isolate one test from other tests uncomment the @tag('temp') above the test then run: 

`docker exec -it django_dev python manage.py test --tag temp`

To run coverage: (To show python code that was not tested.)\
`docker exec -it django_dev coverage run --source='.' manage.py test` \
`docker exec -it django_dev coverage html`

## Troubleshooting:
### SQL Error
![Screenshot of SQL error page](/screenshots/troubleshoot_sql-error.png?raw=true "SQL Error Screenshot")
If you encounter this SQL error when attempting to access https://0.0.0.0:8000/, there may be updates to the database, so you will need to migrate the database again. Follow these steps:
1. Make sure the server is running using `docker compose up`.
1. Open a new console window and run `docker exec -it django_dev python manage.py migrate`.
1. Access https://0.0.0.0:8000/ and the issue should hopefully be resolved!

### Docker Desktop
While not necessary, you may find it helpful to install the [Docker Desktop](https://www.docker.com/products/docker-desktop/) UI to manage your containers. If there are build-related issues, try clearing your containers, images, volumes, and builds.