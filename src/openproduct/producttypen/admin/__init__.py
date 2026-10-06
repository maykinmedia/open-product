from .actie import ActieInline
from .bestand import BestandAdmin
from .content import ContentElementTranslationAdmin, ContentLabelAdmin
from .dmn_config import DmnConfigAdmin
from .facet import FacetTypeAdmin
from .jsonschema import JsonSchemaAdmin
from .link import LinkAdmin
from .prijs import PrijsAdmin
from .producttype import ProductTypeAdmin
from .thema import ThemaAdmin
from .upn import UniformeProductNaamAdmin

__all__ = [
    "ActieInline",
    "BestandAdmin",
    "ContentElementTranslationAdmin",
    "ContentLabelAdmin",
    "DmnConfigAdmin",
    "FacetTypeAdmin",
    "JsonSchemaAdmin",
    "LinkAdmin",
    "PrijsAdmin",
    "ProductTypeAdmin",
    "ThemaAdmin",
    "UniformeProductNaamAdmin",
]
