FROM python:3.7.3-slim

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip3 install -r requirements.txt && pip3 install gunicorn json-logging-py

COPY . /api

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/api/gunicorn.py", "--log-config", "/api/logging.conf", "-b", ":5000", "server:app"]
