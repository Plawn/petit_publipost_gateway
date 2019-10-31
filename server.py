"""Main app for api-doc 
REQUIRES CONF_FILE to be set to the configuration file
it must be a yaml and include


MINIO_HOST": "<host>"
MINIO_KEY": "<>"
MINIO_PASS": "<>"
manifest: 
    <template_bucket_name>:
        # output bucket         
        <output_bucket>: new-output         
        # thats the name under which the document will be usable         
        type: mission

"""

import yaml
import json
import os
import shutil
import traceback
from typing import Dict, Union

from flask import Flask, jsonify, request

from app import MinioCreds, MinioPath, TemplateDB
from datetime import timedelta


# should be env or config variable
TIME_DELTA = timedelta(days=1)
TEMP_DIR = 'temp'
MANIFEST_TOKEN = 'manifest'

if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.mkdir(TEMP_DIR)


conf_filename: str = os.environ['CONF_FILE']

with open(conf_filename, 'r') as f:
    settings: Dict[str, object] = yaml.load(f)

manifest = settings[MANIFEST_TOKEN]

minio_creds = MinioCreds(
    settings['MINIO_HOST'],
    settings['MINIO_KEY'],
    settings['MINIO_PASS'])

engine_settings = settings['engine_settings']

template_db = TemplateDB(manifest, engine_settings,TIME_DELTA, TEMP_DIR, minio_creds)

app = Flask(__name__)


# daw working
@app.route('/document', methods=['GET'])
def get_all():
    return jsonify(template_db.to_json())


# das working
@app.route('/document/<_type>', methods=['GET'])
def get_all_documents_from_type(_type: str):
    if _type in template_db.templators:
        return jsonify(template_db.templators[_type].to_json())
    else:
        return jsonify({'error': 'Type not found'}), 404


# das working
@app.route('/document/<_type>/<name>', methods=['GET'])
def get_fields_document(_type: str, name: str):
    # check if type exists
    if _type in template_db.templators:
        # check if template name exists
        if name in template_db.templators[_type].templates:
            return jsonify(template_db.templators[_type].templates[name].to_json())
        return jsonify({'error': 'Template does not exists'}), 404
    else:
        return jsonify({'error': 'Type not found'}), 404


# das working
@app.route('/reload', methods=['GET'])
def reload_document():
    try:
        template_db.init()
        return jsonify({'error': False})
    except:
        return jsonify({'error': traceback.format_exc()}), 500


# das working
# data sould of the form :
# {
#   $type1 : {
#           $field_name1 : $value1,
#           $field_name2 : $value2,
#           }
#   $type2 : {
#           $field_name1 : $value1,
#           $field_name2 : $value2,
#           }
# }
@app.route('/publipost', methods=['POST'])
def publipost_document():
    form: Dict[str, Union[str, Dict[str, str]]] = request.get_json()
    _type: str = form['type']
    document_name: str = form['document_name']
    filename: str = form['filename']
    data: Dict[str, Dict[str, str]] = form['data']
    return jsonify({
        'url': template_db.render_template(_type, document_name, data, filename)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
