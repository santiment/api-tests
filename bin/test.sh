#! /bin/sh

docker build -t api-test . &&
docker run --rm -t api-test python cli.py projects bitcoin
