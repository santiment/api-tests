FROM python:3.7.4-slim as builder

RUN apt-get -yqq update \
&& apt-get -yqq install gcc

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 wheel -r requirements.txt -w /wheels

FROM python:3.7.4-slim
RUN apt-get -yqq update \
&& apt-get -yqq install gcc

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt --find-links /wheels

COPY . /app
ENV PYTHONPATH /app

WORKDIR /app

CMD ["python", "cli.py", "top"]