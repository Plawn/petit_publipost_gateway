"""Main app for api-doc 
REQUIRES CONF_FILE to be set to the configuration file
it must be a yaml and include

"""

import json
import os
import shutil
import traceback
from datetime import timedelta
from typing import Dict, Union, List
from dataclasses import dataclass

import yaml
from flask import Flask, jsonify, request

from .ressources import TEMP_DIR, template_db
from .template_db import MinioCreds, MinioPath, TemplateDB, from_strings_to_dict, template_engine, RenderOptions, ENSURE_KEYS

default_options = RenderOptions(push_result=True, compile_options=[ENSURE_KEYS], transform_data=True)

app = Flask(__name__)


def using_loaded_db(func):
    name = func.__name__

    def f(*args, **kwargs):
        if template_db.loading:
            return jsonify({'error': 'db is not loaded'}), 400
        return func(*args, **kwargs)
    f.__name__ = name
    return f


@app.route('/document', methods=['GET'])
@using_loaded_db
def get_all():
    return jsonify(template_db.to_json())


@app.route('/document/<_type>', methods=['GET'])
@using_loaded_db
def get_all_documents_from_type(_type: str):
    if _type in template_db.templators:
        return jsonify(template_db.templators[_type].to_json())
    else:
        return jsonify({'error': 'Type not found'}), 404


@app.route('/document/<_type>/<name>', methods=['GET'])
@using_loaded_db
def get_fields_document(_type: str, name: str):
    # check if type exists
    if _type in template_db.templators:
        # check if template name exists
        if name in template_db.templators[_type].templates:
            return jsonify(template_db.templators[_type].templates[name].get_fields())
        return jsonify({'error': 'Template does not exists'}), 404
    else:
        return jsonify({'error': 'Type not found'}), 404


# das working
@app.route('/reload/<templator_name>/<name>', methods=['GET'])
def reload_document(templator_name: str, name: str):
    try:
        if name == 'all':
            successes, fails = template_db.templators[templator_name].pull_templates(
            )
            return jsonify({'error': False})
        else:
            # should be full name
            # ex: DDE.docx
            return jsonify(template_db.templators[templator_name].pull_template(name))
    except KeyError as e:
        return jsonify({'error': f'Template not found {e.__str__()}'}), 400
    except:
        return jsonify({'error': traceback.format_exc()}), 500


@app.route('/reload', methods=['GET'])
def reload_all_documents():
    try:
        template_db.load_templates()
        return jsonify({'error': False})
    except:
        return jsonify({'error': traceback.format_exc()}), 500


@app.route('/publipost', methods=['POST'])
@using_loaded_db
def publipost_document():
    form: Dict[str, Union[str, Dict[str, str]]] = request.get_json()

    _type: str = form['type']
    document_name: str = form['template_name']
    filename: str = form['filename']
    options:RenderOptions = form.get('options', default_options)
    data = form['data']
    
    # if we want to get the result back directly we can set the push_result to False
    # for email rendering we will use the push_result option
    return jsonify({
        'result': template_db.render_template(_type, document_name, data, filename, options)
    })


@app.route('/live', methods=['GET'])
def live():
    return 'OK', 200


@app.route('/is_db_loaded', methods=['GET'])
def is_db_loaded():
    return jsonify({'loaded': template_db.loading})


@app.route("/status", methods=['GET'])
def status():
    return jsonify({
        engine_name: (engine_name in template_db.engines and engine.is_up() ) for engine_name, engine in template_engine.template_engines.items()
    })
