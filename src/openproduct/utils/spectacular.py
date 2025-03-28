from sys import stdout

from drf_spectacular.plumbing import (
    get_lib_doc_excludes as default_get_lib_doc_excludes,
)


def custom_postprocessing_hook(result, generator, request, public):
    """
    DRF Spectacular adds default = [] to the item inside an array on PrimaryKeyRelatedField fields with many=True like

    `producttype_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        default=[],
        write_only=True,
        source="producttypen",
    )`
    (src/openproduct/producttypen/serializers/thema.py)

    This generates the following schema:

    producttype_ids:
      type: array
      items:
        type: string
        format: uuid
        writeOnly: true     # duplicate
        default: []         # duplicate and incorrect as the values in the array are type: string
      writeOnly: true
      default: []           # correct, type array has default: []
    """

    schemas = result.get("components", {}).get("schemas", {})

    for schema_key, schema in schemas.items():
        properties = schema.get("properties", {})

        for prop_key, prop in properties.items():
            default = prop.get("default", None)
            if isinstance(default, list):
                stdout.write(f"removed default=[] from {schema_key}.{prop_key}\n")
                items = prop.get("items", {})
                items.pop("default", None)
                items.pop("writeOnly", None)

    return result


def get_lib_doc_excludes():
    """
    Exclude AuditTrailViewSetMixin docstring from api spec generation
    """
    from openproduct.logging.api_tools import AuditTrailViewSetMixin

    return default_get_lib_doc_excludes() + [AuditTrailViewSetMixin]
