FROM python:3.7.2-slim

WORKDIR /api

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

# need to add a real wsgi server after
ENTRYPOINT ["python3", "start.py", "5000"]
