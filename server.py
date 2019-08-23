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
from typing import Dict
import json
import os

TEMP_DIR = 'temp'

with open(os.environ['CONF_FILE'], 'r') as f :
    settings = json.load(f)

manifest_path = MinioPath(settings['SETTINGS_BUCKET'], settings['MANIFEST_FILE'])

creds = MinioCreds(settings['MINIO_HOST'], settings['MINIO_KEY'], settings['MINIO_PASS'])
db = TemplateDB(manifest_path, TEMP_DIR, creds)

app = Flask(__name__)

# das working
@app.route('/get_all_documents/<_type>')
def get_all_documents_from_type(_type: str): 
    return jsonify(db.templators[_type].to_json())


@app.route('/get_all')
def get_all(): return jsonify(db.to_json())


# das working
@app.route('/get_fields_document/<_type>/<name>')
def get_fields_document(_type: str, name: str):
    if _type in db.templators:
        if name in db.templators[_type].templates:
            return jsonify(db.templators[_type].templates[name].to_json())
    else:
        return jsonify({'error': 404}), 404

# das working
@app.route('/reload')
def reload_document():
    db._init()
    return jsonify({'error': False})


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
    _type = request.form['type']
    document_name: str = request.form['document_name']
    filename: str = request.form['filename']
    data: Dict[str, Dict[str, str]] = json.loads(request.form['data'])
    return jsonify({'url': db.render_template(_type, document_name, data, filename)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
