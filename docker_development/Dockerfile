FROM python:3

ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
COPY wpa_project/wpa_project.env /code/.env
RUN pip install -r requirements.txt
#COPY ../wpa_project /code/
