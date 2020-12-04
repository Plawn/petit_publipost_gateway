"""Main app for api-doc 
REQUIRES CONF_FILE to be set to the configuration file
it must be a yaml and include

"""

import traceback
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .ressources import template_db
from .template_db import (ENSURE_KEYS, MinioCreds, MinioPath, RenderOptions,
                          TemplateDB, from_strings_to_dict, template_engine)
from .template_db.template_engine.base_template_engine import EngineDown

default_options = RenderOptions(
    push_result=True,
    compile_options=[
        ENSURE_KEYS
    ],
    transform_data=True
)

app = FastAPI(
    on_startup=[
        lambda: template_db.init()
    ]
)


def make_error(msg: str, code: int = 500):
    return HTTPException(code, {'error': msg})


@app.get('/document')
def get_all():
    return template_db.to_json()


@app.get('/document/{_type}')
def get_all_documents_from_type(_type: str):
    if _type in template_db.templators:
        return template_db.templators[_type].to_json()
    else:
        return make_error('Type not found', 404)


@app.get('/document/{_type}/{name}')
def get_fields_document(_type: str, name: str):
    # check if type exists
    if _type in template_db.templators:
        # check if template name exists
        if name in template_db.templators[_type].templates:
            return template_db.templators[_type].templates[name].get_fields()
        return make_error('Template not found', 404)
    else:
        return make_error('Type not found', 404)


# das working
@app.get('/reload/{templator_name}/{name}')
def reload_document(templator_name: str, name: str):
    try:
        if name == 'all':
            successes, fails = template_db.templators[templator_name].pull_templates(
            )
            return {'error': False}
        else:
            # should be full name
            # ex: DDE.docx
            return template_db.templators[templator_name].pull_template(name)
    except KeyError as e:
        return make_error(f'Template not found {e.__str__()}', 400)
    except:
        return make_error(traceback.format_exc(), 500)


@app.route('/reload', methods=['GET'])
def reload_all_documents():
    try:
        template_db.load_templates()
        return {'error': False}
    except:
        return make_error(traceback.format_exc(), 500)


class PubliPostBody(BaseModel):
    type: str
    document_name: str
    filename: str
    options: Optional[RenderOptions]
    data: dict


@app.post('/publipost')
def publipost_document(body: PubliPostBody):

    options = body.options or default_options
    data = body.data
    if options.transform_data:
        data: Dict[str, object] = from_strings_to_dict(body.data)
    # if we want to get the result back directly we can set the push_result to False
    # for email rendering we will use the push_result option
    try:
        return {
            'result': template_db.render_template(body.type, body.document_name, data, body.filename, options)
        }
    except EngineDown:
        return make_error('Engine down')
    except:
        traceback.print_exc()
        return make_error('Unknown error')


@app.get('/live')
def live():
    return 'OK', 200


@app.get('/is_db_loaded')
def is_db_loaded():
    return {'loaded': template_db.loading}


@app.get("/status")
def status():
    return {
        engine_name: (engine_name in template_db.engines and engine.is_up())
        for engine_name, engine in template_engine.template_engines.items()
    }


@app.get('/status/{engine_name}')
def engine_status(engine_name: str):
    if engine_name in template_db.engines:
        if template_db.engines[engine_name].is_up():
            return 'OK', 200

        else:
            return 'KO', 402
    else:
        return 'KO', 404
