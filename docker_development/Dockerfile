FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y enchant-2 myspell-es myspell-ru
WORKDIR /code
COPY requirements.txt /code/
COPY wpa_project/wpa_project.env /code/.env
RUN pip install -r requirements.txt
RUN useradd --user-group --create-home --no-log-init --shell /bin/bash app
#COPY ../wpa_project /code/
