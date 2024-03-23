#!/bin/bash

git fetch --all
git reset --hard origin/event
sudo docker-compose build django
sudo docker-compose up -d