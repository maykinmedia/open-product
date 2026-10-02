DMN_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "$defs": {
        "classType": {
            "type": "string",
            "enum": ["String", "Integer", "Double", "Boolean", "Date", "Long"],
        },
        "jsonPathString": {
            "type": "string",
            "description": "A JSONPath expression, must start with $.",
            "pattern": r"^\$\..+",
        },
    },
    "properties": {
        "static": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "classType", "value"],
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "classType": {"$ref": "#/$defs/classType"},
                },
                "additionalProperties": False,
            },
        }
    },
    "additionalProperties": {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["name", "classType", "regex"],
            "properties": {
                "name": {"type": "string"},
                "regex": {"$ref": "#/$defs/jsonPathString"},
                "classType": {"$ref": "#/$defs/classType"},
            },
            "additionalProperties": False,
        },
    },
}

API_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "variabelen": {
            "type": "object",
            "description": "Mapping of category name to a set of variable-name -> JSONPath mappings",
            "additionalProperties": {"$ref": "#/$defs/variabeleMap"},
            "minProperties": 1,
        },
        "static": {
            "type": "object",
            "description": "Flat mapping of static key/value string pairs",
            "additionalProperties": {"type": "string"},
            "minProperties": 1,
        },
    },
    "required": ["variabelen"],
    "additionalProperties": False,
    "$defs": {
        "variabeleMap": {
            "type": "object",
            "description": "Mapping of variable name (dot notation) to a JSONPath expression",
            "additionalProperties": {"$ref": "#/$defs/jsonPathString"},
            "minProperties": 1,
        },
        "jsonPathString": {
            "type": "string",
            "description": "A JSONPath expression, must start with $.",
            "pattern": r"^\$\..+",
        },
    },
}

FORM_SCHEMA = API_SCHEMA
