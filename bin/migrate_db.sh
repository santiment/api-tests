#! /bin/sh

docker-compose build && \
docker-compose run api-tests python cli.py migrate_db