#! /bin/sh

docker build --build-arg PYTHON_ENV=test -t api-test . &&
docker run --rm -t api-test python cli.py projects bitcoin
