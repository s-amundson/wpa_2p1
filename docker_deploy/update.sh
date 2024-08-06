#!/bin/bash

git fetch --all
git reset --hard origin/nonce_issue
sudo docker-compose build django
sudo docker-compose up -d