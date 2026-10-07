from ..utils.spectacular import SerializerJSONFieldExtension, register
from .schemas import API_SCHEMA, DMN_SCHEMA


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
                # API and FORMULIER use the same schema for now.
                register(auto_schema, "ApiOrFormMapping", API_SCHEMA),
            ],
            "description": (
                "Schema depends on `type`: `dmn` → DmnMapping; "
                "`api` and `formulier` → ApiMapping."
            ),
        }
