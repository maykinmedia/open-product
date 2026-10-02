from functools import cache

from django.utils.module_loading import import_string

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import ResolvedComponent, append_meta
from rest_framework import serializers

from .schemas import API_SCHEMA, DMN_SCHEMA


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


class PrijsRegelMappingExtension(SerializerJSONFieldExtension):
    serializer_class = "openproduct.producttypen.serializers.prijs.PrijsRegelSerializer"
    field_name = "mapping"

    def get_schema(self, auto_schema, direction):
        return register(auto_schema, "DmnMapping", DMN_SCHEMA)


class ActieMappingExtension(SerializerJSONFieldExtension):
    serializer_class = "openproduct.producttypen.serializers.actie.ActieSerializer"
    field_name = "mapping"

    def get_schema(self, auto_schema, direction):
        return {
            "oneOf": [
                register(auto_schema, "DmnMapping", DMN_SCHEMA),
                # API and FORMULIER currently share one schema; listing both would break oneOf
                register(auto_schema, "ApiOrFormMapping", API_SCHEMA),
            ],
            "description": (
                "Schema depends on `type`: `dmn` → DmnMapping; "
                "`api` and `formulier` → ApiMapping."
            ),
        }
