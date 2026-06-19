from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase, override_settings

from openproduct.producttypen.tests.factories import JsonSchemaFactory
from openproduct.utils.jsonschema_validators import (
    validate_jsonschema,
)

SCHEMA_ALL_FORMATS = {
    "type": "object",
    "properties": {
        "color": {"type": "string", "format": "color"},
        "date": {"type": "string", "format": "date"},
        "date-time": {"type": "string", "format": "date-time"},
        "duration": {"type": "string", "format": "duration"},
        "email": {"type": "string", "format": "email"},
        "hostname": {"type": "string", "format": "hostname"},
        "idn-hostname": {"type": "string", "format": "idn-hostname"},
        "ipv4": {"type": "string", "format": "ipv4"},
        "ipv6": {"type": "string", "format": "ipv6"},
        "iri": {"type": "string", "format": "iri"},
        "iri-reference": {"type": "string", "format": "iri-reference"},
        "json-pointer": {"type": "string", "format": "json-pointer"},
        "regex": {"type": "string", "format": "regex"},
        "relative-json-pointer": {"type": "string", "format": "relative-json-pointer"},
        "time": {"type": "string", "format": "time"},
        "uri": {"type": "string", "format": "uri"},
        "uri-reference": {"type": "string", "format": "uri-reference"},
        "uri-template": {"type": "string", "format": "uri-template"},
        "uuid": {"type": "string", "format": "uuid"},
    },
}


class TestJsonSchema(TestCase):
    def setUp(self):
        self.schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {
                    "price": {"type": "number"},
                    "name": {"type": "string"},
                },
                "required": ["price", "name"],
            },
        )

    def test_valid_json(self):
        self.schema.validate(
            {
                "price": 10,
                "name": "test",
            }
        )

    def test_invalid_json(self):
        with self.assertRaisesMessage(
            DjangoValidationError, "'price' is a required property"
        ):
            self.schema.validate({"name": "Eggs"})

    def test_invalid_json_wrong_type(self):
        with self.assertRaisesMessage(
            DjangoValidationError, "'not-a-number' is not of type 'number'"
        ):
            self.schema.validate({"price": "not-a-number", "name": "Eggs"})

    def test_invalid_json_missing_all_required(self):
        with self.assertRaisesMessage(
            DjangoValidationError, "'price' is a required property"
        ):
            self.schema.validate({})

    def test_clean_with_invalid_schema(self):
        invalid_cases = [
            ({"type": []}, "[] is not valid under any of the given schemas"),
            (
                {"type": "invalid-type"},
                "'invalid-type' is not valid under any of the given schemas",
            ),
            (
                {"properties": "not-an-object"},
                "'not-an-object' is not of type 'object'",
            ),
            ({"required": "not-an-array"}, "'not-an-array' is not of type 'array'"),
        ]

        for invalid_schema, expected_reason in invalid_cases:
            with self.subTest(schema=invalid_schema):
                self.schema.schema = invalid_schema
                with self.assertRaisesMessage(DjangoValidationError, expected_reason):
                    self.schema.clean()

    def test_clean_with_valid_schema(self):
        self.schema.clean()

    def test_clean_with_draft202012_schema(self):
        self.schema.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "price": {"type": "number"},
            },
            "required": ["price"],
        }
        self.schema.clean()

    def test_validate_without_schema_uri_falls_back_to_latest_draft(self):
        self.schema.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        self.schema.validate({"name": "test"})

    @override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=True)
    def test_validate_format_checker_enabled(self):
        self.schema.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
            },
            "required": ["email"],
        }

        with self.assertRaises(DjangoValidationError):
            self.schema.validate({"email": "not-an-email"})

    @override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=False)
    def test_validate_format_checker_disabled(self):
        self.schema.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
            },
            "required": ["email"],
        }

        self.schema.validate({"email": "not-an-email"})


class JSONSchemaFormatTests(TestCase):
    def test_color(self):
        data = {}
        invalid_values = ["#12", "#12345", "#zzzzzz", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["color"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        validate_jsonschema({"color": "#ff0000"}, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"color": "red"}, SCHEMA_ALL_FORMATS)

    def test_date(self):
        data = {}
        invalid_values = ["2026-13-40", None, 123, "test"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["date"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"date": "2026-01-01"}, SCHEMA_ALL_FORMATS)

    def test_date_time(self):
        data = {}
        invalid_values = ["2026-13-40T25:61:61Z", None, 123, "test"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["date-time"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"date-time": "2026-01-01T12:34:56Z"}, SCHEMA_ALL_FORMATS)

    def test_duration(self):
        data = {}
        invalid_values = ["not-a-duration", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["duration"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"duration": "P3Y6M4DT12H30M5S"}, SCHEMA_ALL_FORMATS)

    def test_email(self):
        data = {}
        invalid_values = ["test", None, "123", 123, "test-test@.test"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["email"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        validate_jsonschema({"email": "test@example.com"}, SCHEMA_ALL_FORMATS)

    def test_hostname(self):
        data = {}
        invalid_values = ["-invalid-host", "invalid_host", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["hostname"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"hostname": "example.com"}, SCHEMA_ALL_FORMATS)

    def test_idn_hostname(self):
        data = {}
        invalid_values = ["-invalid.com", "invalid-.com", "inv@lid.com", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["idn-hostname"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_values = ["münchen.com", "tęst.com", "crème.fr"]
        for val in valid_values:
            data["idn-hostname"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_ipv4(self):
        data = {}
        invalid_values = ["999.999.999.999", "abc.def.ghi.jkl", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["ipv4"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"ipv4": "192.168.1.1"}, SCHEMA_ALL_FORMATS)

    def test_ipv6(self):
        data = {}
        invalid_values = ["invalid:ipv6", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["ipv6"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema(
            {"ipv6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}, SCHEMA_ALL_FORMATS
        )

    def test_iri(self):
        data = {}
        invalid_values = ["http://exa mple.com", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["iri"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_values = ["https://example.com", "https://münchen.com/über"]
        for val in valid_values:
            data["iri"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_iri_reference(self):
        data = {}
        invalid_refs = ["ht tp://example.com", "://missing.scheme.com", None, 123]
        for val in invalid_refs:
            with self.assertRaises(DjangoValidationError):
                data["iri-reference"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)

        valid_refs = ["/relative/path", "crème/cheese", "münchen/über"]
        for val in valid_refs:
            data["iri-reference"] = val
            validate_jsonschema(data, SCHEMA_ALL_FORMATS)

    def test_json_pointer(self):
        data = {}
        invalid_values = ["foo/bar", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["json-pointer"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"json-pointer": "/foo/bar"}, SCHEMA_ALL_FORMATS)

    def test_regex(self):
        data = {}
        invalid_values = ["[unclosed", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["regex"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"regex": "^[a-z]+$"}, SCHEMA_ALL_FORMATS)

    def test_relative_json_pointer(self):
        data = {}
        invalid_values = ["foo", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["relative-json-pointer"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"relative-json-pointer": "0/foo"}, SCHEMA_ALL_FORMATS)

    def test_time(self):
        data = {}
        invalid_values = ["25:61:61", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["time"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"time": "12:34:56Z"}, SCHEMA_ALL_FORMATS)

    def test_uri(self):
        data = {}
        invalid_values = ["not-a-uri", "://missing", None, 123]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uri"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri": "https://example.com/path"}, SCHEMA_ALL_FORMATS)

    def test_uri_reference(self):
        data = {}
        invalid_values = [None, 123, "http://[invalid"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uri-reference"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri-reference": "/relative/path"}, SCHEMA_ALL_FORMATS)

    def test_uri_template(self):
        data = {}
        invalid_values = [None, 123, "{unclosed"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uri-template"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema({"uri-template": "/users/{id}"}, SCHEMA_ALL_FORMATS)

    def test_uuid(self):
        data = {}
        invalid_values = ["not-a-uuid", None, 123, "1234"]
        for val in invalid_values:
            with self.assertRaises(DjangoValidationError):
                data["uuid"] = val
                validate_jsonschema(data, SCHEMA_ALL_FORMATS)
        validate_jsonschema(
            {"uuid": "123e4567-e89b-12d3-a456-426614174000"}, SCHEMA_ALL_FORMATS
        )
