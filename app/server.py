"""Main app for api-doc 
REQUIRES CONF_FILE to be set to the configuration file
it must be a yaml and include

"""

import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .ressources import template_db
from .template_db import (ENSURE_KEYS, EngineDown, RenderOptions,
                          from_strings_to_dict, template_engine)

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
    """Formats error as JSON message
    """
    return HTTPException(code, {'error': msg})


@app.get('/document')
def get_all():
    """Returns the full content of the templateDB, 
    all templators and their given templates
    """
    return template_db.to_json()


@app.get('/document/{templator_name}')
def get_all_documents_from_type(templator_name: str):
    """Returns all the template from a given templator
    """
    templator = template_db.get_templator(templator_name)
    if templator is not None:
        return templator.to_json()
    else:
        return make_error('Type not found', 404)


@app.get('/document/{templator_name}/{name}')
def get_fields_document(templator_name: str, name: str):
    """Returns all the fields for a given template in a templator
    """
    templator = template_db.get_templator(templator_name)
    if templator is not None:
        # check if template name exists
        if name in templator.templates:
            res = template_db.templators[templator_name].templates[name].get_fields()
            if res is None:
                return make_error('Template contains error', 400)
        return make_error('Template not found', 404)
    else:
        return make_error('Templator not found', 404)


@app.get('/reload/{templator_name}/{template_name}')
def reload_document(templator_name: str, template_name: str):
    """Will reload the specied templator in the case name `template_name` == 'all'

    else will reload the template_name from a given templator
    """
    try:
        templator = template_db.get_templator(templator_name)
        if templator_name is not None:
            if template_name == 'all':
                templator.pull_templates()
                return {'error': False}
            else:
                # should be full name
                # ex: DDE.docx
                return templator.pull_template(template_name)
        else:
            return make_error(f'Template not found {templator_name}', 404)
    except:
        return make_error(traceback.format_exc(), 500)


@app.get('/reload')
def reload_all_documents():
    """Will attempt to reload the complete db
    """
    try:
        template_db.load_templates()
        return {'error': False}
    except:
        return make_error(traceback.format_exc(), 500)

# TODO:
# update in phoenix-api the name of the fields for a better comprehension


class PubliPostBody(BaseModel):
    # templator name
    templator_name: str
    # template_name
    template_name: str

    """output_filename in case of option.push_result = False"""
    output_filename: str
    """render options that will be passed to the template_db and engines"""
    options: Optional[RenderOptions]
    """the actual data to replace in the templates"""
    data: Dict[str, Any]


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
            'result': template_db.render_template(body.templator_name, body.template_name, data, body.output_filename, options)
        }
    except EngineDown:
        return make_error('Engine down')
    except Exception as e:
        traceback.print_exc()
        return make_error(f'Unknown error, {e}')


@app.get('/live')
def live():
    return 'OK', 200


@app.get('/is_db_loaded')
def is_db_loaded():
    return {
        'loaded': template_db.loading
    }


@app.get("/status")
def status():
    """Returns the status of the pool of engines
    """
    return {
        engine_name: (engine_name in template_db.engines and engine.is_up())
        for engine_name, engine in template_engine.template_engines.items()
    }


@app.get('/status/{engine_name}')
def engine_status(engine_name: str):
    """Returns the status of a given engine
    """
    if engine_name in template_db.engines:
        if template_db.engines[engine_name].is_up():
            return 'OK', 200
        else:
            return 'KO', 402
    else:
        return 'KO', 404
