FROM registry.dev.juniorisep.com/pleveau/excel-publiposting:prod as source



FROM python:3.7.3-slim

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip3 install -r requirements.txt && pip3 install gunicorn json-logging-py

COPY . /api

COPY --from=source build/ excel_build/
# installing node
RUN apt  update
RUN apt install -y curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN apt install -y nodejs
RUN npm install yarn
RUN cd excel_build && yarn install




EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/api/gunicorn.py", "--log-config", "/api/logging.conf", "-b", ":5000", "server:app"]
