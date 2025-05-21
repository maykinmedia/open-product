from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from rest_framework import serializers

from openproduct.producttypen.models import JsonSchema


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "schema response",
            value={
                "naam": "parkeervergunning-verbruiksobject",
                "schema": {
                    "type": "object",
                    "properties": {"uren": {"type": "number"}},
                    "required": ["uren"],
                },
            },
            response_only=True,
        ),
        OpenApiExample(
            "schema request",
            value={
                "naam": "parkeervergunning-verbruiksobject",
                "schema": {
                    "type": "object",
                    "properties": {"uren": {"type": "number"}},
                    "required": ["uren"],
                },
            },
            request_only=True,
        ),
    ],
)
class JsonSchemaSerializer(serializers.ModelSerializer):
    schema = serializers.DictField()

    def validate_schema(self, schema):
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as e:
            raise serializers.ValidationError(e.message)

        return schema

    class Meta:
        model = JsonSchema
        fields = ("naam", "schema")
