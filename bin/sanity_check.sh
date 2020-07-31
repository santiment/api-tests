#! /bin/sh

docker build --build-arg PYTHON_ENV=test -t api-tests-sanity-check . &&
docker run --rm -e API_KEY=$API_KEY -t api-tests-sanity-check python cli.py projects bitcoin
