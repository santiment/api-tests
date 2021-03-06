FROM python:3.7.4-slim as builder

ARG PYTHON_ENV=production
ARG API_KEY

ENV PYTHON_ENV=${PYTHON_ENV}
ENV API_KEY=${API_KEY}

WORKDIR /app

RUN apt update && apt install gcc libpq-dev -y

COPY requirements.txt /app/requirements.txt
RUN pip3 wheel -r requirements.txt -w /wheels

FROM python:3.7.4-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt --find-links /wheels

COPY . /app

ENV PYTHONPATH /app

WORKDIR /app

CMD ["gunicorn", "app:APP", "--worker-class=gevent", "--workers=2", "-b=0.0.0.0:3000", "--log-level=info"]
