from typing import Any, Dict, Optional

from pydantic import BaseModel

from .template_db import RenderOptions


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
