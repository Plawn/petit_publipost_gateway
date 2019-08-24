"""Main app for api-doc 
REQUIRES CONF_FILE to be set to the configuration file
it must be a json and include

{
    "MINIO_HOST":"<host>",
    "MINIO_KEY":"<>",
    "MINIO_PASS":"<>",
    "SETTINGS_BUCKET":"<>",
    "MANIFEST_FILE":"<>"
}
"""


from flask import Flask, request, jsonify
from app import TemplateDB, MinioCreds, MinioPath
from typing import Dict, Union
import json
import os
import traceback

TEMP_DIR = 'temp'

conf_filename: str = os.environ['CONF_FILE']

with open(conf_filename, 'r') as f:
    settings: Dict[str, str] = json.load(f)

manifest_path = MinioPath(
    settings['SETTINGS_BUCKET'],
    settings['MANIFEST_FILE'])

minio_creds = MinioCreds(
    settings['MINIO_HOST'],
    settings['MINIO_KEY'],
    settings['MINIO_PASS'])

template_db = TemplateDB(manifest_path, TEMP_DIR, minio_creds)

app = Flask(__name__)


# das working
@app.route('/get_all_documents/<_type>', methods=['GET'])
def get_all_documents_from_type(_type: str):
    return jsonify(template_db.templators[_type].to_json())


# daw working
@app.route('/get_all', methods=['GET'])
def get_all():
    return jsonify(template_db.to_json())


# das working
@app.route('/get_fields_document/<_type>/<name>', methods=['GET'])
def get_fields_document(_type: str, name: str):
    # check if type exists
    if _type in template_db.templators:
        # check if template name exists
        if name in template_db.templators[_type].templates:
            return jsonify(template_db.templators[_type].templates[name].to_json())
        return jsonify({'error': 404}), 404
    else:
        return jsonify({'error': 404}), 404


# das working
@app.route('/reload', methods=['GET'])
def reload_document():
    try:
        template_db._init()
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
    return jsonify({'url': template_db.render_template(_type, document_name, data, filename)})


if __name__ == '__main__':
    app.run(host='0.0.0.0')