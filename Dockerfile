FROM registry.dev.juniorisep.com/pleveau/excel-publiposting:prod as source



FROM python:3.7.3-slim

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip3 install -r requirements.txt && pip3 install gunicorn json-logging-py

COPY . /api

COPY --from=source /api/build/ excel_build/
# installing node
RUN apt update
RUN apt install -y curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_11.x  | bash -
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - 
RUN echo deb "https://dl.yarnpkg.com/debian/stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

RUN apt update && sudo apt install yarn
RUN apt install -y nodejs

# building server
RUN cd excel_build && yarn install

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/api/gunicorn.py", "--log-config", "/api/logging.conf", "-b", ":5000", "server:app"]
