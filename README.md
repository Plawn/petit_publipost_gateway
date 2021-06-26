# Petit publiposter

## Docker Setup

PLS mount the conf file into /api/conf.yaml

## Installation

```sh
pip install -r requirements.txt
```

Install the wanted engines

## How to start

```sh
./start_dev.sh
```

Start the wanted engines

### Avec docker

```sh
docker-compose up
```

Il vous faut un fichier de configuration valide qui sera monté dans le volume docker

## Configuration

The configuration is supposed to be in the `conf.yaml` file

```yaml
# should be imported from the minio creds conf file

s3:
  host: <>
  accessKey: <>
  passKey: <>
  secure: true

cache_validation_interval: 60 # cache will be validated every minute

push_result_validity_time: 86400 #seconds, it's a day

engine_settings:
  docx:
    host: localhost:3002
    secure: false
  xlsx:
    host: localhost:3001
    secure: false
  pptx:
    host: localhost:3003
    secure: false

manifest:
  new-templates:
    output_bucket: temporary
    # thats the name under which the document will be accessible
    export_name: example

```

Note: **Don't forget to put the template in the correct bucket**

## Summary

This gateway is a part of the petite stack and is meant to be used with the petit_engines in order to publipost document. It uses publipost engines accross the network in order to make it simpler to add new engines later. It does pattern transformation for all the engines and maps the template depending on their extension. In order to use a given engine you have to use a connector and the corresponding engine.
In order to be flexible and modular the the templates can be placed on an S3 provider. As of now, the result of the publiposting operation is sent to the S3 service in order to avoid unecessary network usage.

## Endpoints

### Publipost

POST: /publipost

Example

<!-- TODO fix -->
```json
 {
    "data":  {
        "mission": {
            "contact.civility.value":"JEB",
            "contact.name":"Test",
        },
        "student":{
            "name.value":"Paul"
        },
    },
    "template_name": "DDE",
    "filename": "test.docx",
    "type": "phoenix"
}
```

#### `data`

The data to publipost

#### `template_name`

Self explenatory ?

#### `type`

We will have multiple document repositories from now on, ex: (tresorerie, ...etc)

#### `filename`

That's the desired filename save, that's the previous `generated_name`

### Get placeholders

On fait un get sur "/document/{bucketName}/{templateName}"

ça renvoie donc :

```json
{
    "mission": [
        "previousDocumentReference(\"ARM\")",
        "StudentDocRef(#student,\"REM\")",
        "documentReference(\"AEN\")"
    ],
    "student": [
        "city",
        "address",
        "civility.value",
        "firstName",
        "zipCode",
        "lastName"
    ]
}
```

### healtcheck

GET /live

## Adding a new engine

Use either the [petit_nodejs_publipost_connector](https://github.com/Plawn/petit_nodejs_publipost_connector) for nodejs or the [petit_python_publipost_connector](https://github.com/Plawn/petit_python_publipost_connector) for python, and implement the template interface. Then create a connector using, makeConnector or make_connector.

This engines are available today:

- [petit_docx_engine](https://github.com/Plawn/petit_docx_engine)   (python)
- [petit_xlsx_engine](https://github.com/Plawn/petit_xlsx_engine)   (nodejs)
- [petit_pptx_engine](https://github.com/Plawn/petit_pptx_engine)   (nodejs)
- [petit_html_engine](https://github.com/Plawn/petit_html_engine)   (python)
- [petit_pdf_engine](https://github.com/Plawn/petit_pdf_engine)     (nodejs)

## Options

### Force reaload cache

Hit the /reload endpoint

## Transformers

If you want to transform the keys or the values of the placeholders you can implement transformers in the connector for local transformation or in the adaptater for global adapatation.

Today the supplied adaptater is the sPel adapter. It's meant to be used with the spel expression parser of the Spring framework.

## Architecture

![architecture](./docs/images/main.svg)
