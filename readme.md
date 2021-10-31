###### Project to make site for Woodley Park Archers for student registration. See docker_deploy/privatefiles.txt for settings information.

To run: \
&nbsp;&nbsp; docker-compose build \
&nbsp;&nbsp; docker-compose up

To test: (with coverage)\
&nbsp;&nbsp; docker-compose -f compose_runserver.yml -f compose_test.yml up