from django.core.exceptions import ValidationError
from django.test import TestCase

from openproduct.producttypen.tests.factories import JsonSchemaFactory


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
            ValidationError, "'price' is a required property"
        ):
            self.schema.validate({"name": "Eggs"})

    def test_clean_with_invalid_schema(self):
        self.schema.schema = {"type": []}
        with self.assertRaisesMessage(
            ValidationError, "[] is not valid under any of the given schemas"
        ):
            self.schema.clean()

    def test_clean_with_valid_schema(self):
        self.schema.clean()
