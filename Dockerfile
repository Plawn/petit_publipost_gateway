FROM registry.dev.juniorisep.com/pleveau/excel-publiposting:prod as source



FROM nikolaik/python-nodejs:latest

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip3 install -r requirements.txt && pip3 install gunicorn json-logging-py

COPY . /api

COPY --from=source /api/build/ excel_build/

# building server
RUN cd excel_build && yarn install

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/api/gunicorn.py", "--log-config", "/api/logging.conf", "-b", ":5000", "server:app"]
