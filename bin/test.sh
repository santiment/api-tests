#! /bin/sh

docker build --build-arg PYTHON_ENV=test -t api-test . &&
docker run --rm -e API_KEY=$API_KEY -t api-test python cli.py projects bitcoin
