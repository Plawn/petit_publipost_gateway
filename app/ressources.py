from .template_db import TemplateDB
from .transformers import PHOENIX_NODE_TRANSFORMER
from .utils import get_settings

settings = get_settings()

template_db = TemplateDB(
    settings.manifest,
    settings.engine_settings,
    settings.push_result_validity_time,
    settings.minio,
    node_transformer=PHOENIX_NODE_TRANSFORMER,
    cache_validation_interval=settings.cache_validation_interval
)

template_db.use_default_connectors()