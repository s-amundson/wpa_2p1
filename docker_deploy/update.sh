#!/bin/bash

git fetch --all
git reset --hard origin/master
sudo docker-compose build django
sudo docker-compose up -d