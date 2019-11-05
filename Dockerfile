FROM registry.dev.juniorisep.com/phoenix/excel-publiposting:prod as excel_publiposting

FROM nikolaik/python-nodejs:latest

WORKDIR /api

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . /api/

RUN mkdir modules

COPY --from=excel_publiposting /api/build/ modules/excel-publiposting/

# installing dependencies
# no need to build as the docker is already built
RUN cd excel-publiposting && yarn install

EXPOSE 5000

# need to add a real wsgi server after
ENTRYPOINT ["python3", "start.py"]
