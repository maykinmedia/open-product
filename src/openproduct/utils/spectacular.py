from functools import cache
from sys import stdout

from django.utils.module_loading import import_string
from django.views import View

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import (
    ResolvedComponent,
    append_meta,
    get_lib_doc_excludes as default_get_lib_doc_excludes,
)
from drf_spectacular.views import (
    SpectacularJSONAPIView as _SpectacularJSONAPIView,
    SpectacularYAMLAPIView as _SpectacularYAMLAPIView,
)
from rest_framework import serializers

from .fields import JSONObjectField


def custom_postprocessing_hook(result, generator, request, public):
    """
    DRF Spectacular adds default = [] to the item inside an array on PrimaryKeyRelatedField fields with many=True like

    `producttype_uuids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        default=[],
        write_only=True,
        source="producttypen",
    )`
    (src/openproduct/producttypen/serializers/thema.py)

    This generates the following schema:

    producttype_uuids:
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

            # fix for missing type for nested serializers.
            if "nullable" in prop and "type" not in prop:
                stdout.write(f"added type:object to {schema_key}.{prop_key}\n")
                prop["type"] = "object"

    return result


def get_lib_doc_excludes():
    """
    Exclude AuditTrailViewSetMixin docstring from api spec generation
    """
    from openproduct.logging.api_tools import AuditTrailViewSetMixin

    return default_get_lib_doc_excludes() + [AuditTrailViewSetMixin]


class AllowAllOriginsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class SpectacularYAMLAPIView(AllowAllOriginsMixin, _SpectacularYAMLAPIView):
    """Spectacular YAML API view with Access-Control-Allow-Origin set to allow all"""


class SpectacularJSONAPIView(AllowAllOriginsMixin, _SpectacularJSONAPIView):
    """Spectacular JSON API view with Access-Control-Allow-Origin set to allow all"""


def to_openapi_schema(schema: dict) -> dict:
    """Inline #/$defs refs and drop $-keywords ($schema, $defs, ...)."""
    defs = schema.get("$defs", {})

    def convert(node):
        if isinstance(node, list):
            return [convert(item) for item in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            return convert(defs[node["$ref"].removeprefix("#/$defs/")])
        return {k: convert(v) for k, v in node.items() if not k.startswith("$")}

    return convert(schema)


def register(auto_schema, name: str, schema: dict) -> dict:
    """Register `schema` as components/schemas/<name> and return a $ref to it."""
    component = ResolvedComponent(
        name=name,
        type=ResolvedComponent.SCHEMA,
        object=name,
        schema=to_openapi_schema(schema),
    )
    auto_schema.registry.register_on_missing(component)
    return component.ref


@cache
def _import(path: str):
    return import_string(path)


class SerializerJSONFieldExtension(OpenApiSerializerFieldExtension):
    """Base: match a single JSONField by serializer class + field name."""

    target_class = serializers.JSONField
    match_subclasses = True
    priority = 1

    serializer_class: str | None = None  # dotted path, imported lazily
    field_name: str | None = None

    @classmethod
    def _matches(cls, target) -> bool:
        if cls.serializer_class is None or not super()._matches(target):
            return False
        return getattr(target, "field_name", None) == cls.field_name and isinstance(
            getattr(target, "parent", None), _import(cls.serializer_class)
        )

    def get_schema(self, auto_schema, direction) -> dict:
        raise NotImplementedError

    def map_serializer_field(self, auto_schema, direction):
        # extensions bypass the field meta (nullable, readOnly, etc.), so add it here
        return append_meta(
            self.get_schema(auto_schema, direction),
            auto_schema._get_serializer_field_meta(self.target, direction),
        )


class JSONObjectFieldExtension(OpenApiSerializerFieldExtension):
    """
    Default schema for `JSONObjectField`: an object with arbitrary properties.

    Used instead of `extend_schema_field`, because that takes precedence over all field
    extensions, which would make the more specific (higher priority)
    `SerializerJSONFieldExtension` subclasses impossible.
    """

    target_class = JSONObjectField
    priority = 0

    def map_serializer_field(self, auto_schema, direction):
        # extensions bypass the field meta (nullable, readOnly, etc.), so add it here
        return append_meta(
            {"type": "object", "additionalProperties": True},
            auto_schema._get_serializer_field_meta(self.target, direction),
        )
