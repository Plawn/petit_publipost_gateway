FROM registry.dev.juniorisep.com/phoenix/excel-publiposting:prod as excel_publiposting

FROM nikolaik/python-nodejs:latest

COPY ./requirements.txt /api/requirements.txt

WORKDIR /api

# RUN pip3 install -r requirements.txt && pip3 install gunicorn json-logging-py

COPY . /api

COPY --from=excel_publiposting /api/build/ excel-publiposting/

# installing dependencies
# no need to build as the docker is already built
RUN cd excel-publiposting && yarn install

EXPOSE 5000

# need to add a real wsgi server after
ENTRYPOINT ["python3", "start.py"]
