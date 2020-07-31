#! /bin/sh

docker build --build-arg PYTHON_ENV=test -t api-tests-test -f Dockerfile-test . &&
docker run --rm -t api-tests-test pytest
