from django.core.exceptions import ValidationError
from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openproduct.producttypen.models import JsonSchema
from openproduct.producttypen.tests.factories import JsonSchemaFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestProductTypeSchema(BaseApiTestCase):
    is_superuser = True
    path = reverse_lazy("schema-list")

    def setUp(self):
        super().setUp()
        self.data = {
            "naam": "parkeervergunning-verbruiksobject",
            "schema": {
                "type": "object",
                "properties": {"uren": {"type": "number"}},
                "required": ["uren"],
            },
        }
        self.schema = JsonSchemaFactory.create(schema=self.data["schema"])

        self.detail_path = reverse("schema-detail", args=[self.schema.id])

    def test_read_schema_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "naam")

        self.assertIsNotNone(error)
        self.assertEqual(error["code"], "required")
        self.assertEqual(
            error["reason"],
            _("This field is required."),
        )

    def test_create_schema(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JsonSchema.objects.count(), 2)

        self.assertEqual(response.data, self.data)

    def test_create_invalid_schema(self):
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
                data = self.data | {"schema": invalid_schema}
                response = self.client.post(self.path, data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                error = get_validation_errors(response, "schema")
                self.assertIsNotNone(error)
                self.assertEqual(error["code"], "invalid")
                self.assertEqual(error["reason"], expected_reason)

    def test_create_schema_with_empty_schema_object(self):
        data = {"naam": "leeg-schema", "schema": {}}
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_schema_with_draft202012(self):
        data = self.data | {
            "naam": "draft202012-schema",
            "schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"uren": {"type": "number"}},
                "required": ["uren"],
            },
        }
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["schema"], data["schema"])

    def test_update_schema(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JsonSchema.objects.count(), 1)
        self.assertEqual(JsonSchema.objects.get().naam, "update")

    def test_update_schema_with_invalid_schema_returns_error(self):
        data = self.data | {"schema": {"type": "invalid-type"}}
        response = self.client.put(self.detail_path, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "schema")
        self.assertIsNotNone(error)
        self.assertEqual(error["code"], "invalid")

    @override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=False)
    def test_create_schema_invalid_email_passes(self):
        data = self.data | {
            "naam": "email-schema",
            "schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"email": {"type": "string", "format": "email"}},
                "required": ["email"],
            },
        }
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        schema = JsonSchema.objects.get(naam="email-schema")
        schema.validate({"email": "not-an-email"})

    @override_settings(JSONSCHEMA_USE_FORMAT_CHECKER=True)
    def test_create_schema_invalid_email_fails(self):
        data = self.data | {
            "naam": "email-schema",
            "schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"email": {"type": "string", "format": "email"}},
                "required": ["email"],
            },
        }
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        schema = JsonSchema.objects.get(naam="email-schema")
        with self.assertRaises(ValidationError) as er:
            schema.validate({"email": "not-an-email"}, "schema")
        self.assertEqual(
            str(er.exception),
            "{'schema.email': [\"'not-an-email' is not a 'email'\"]}",
        )

    def test_partial_update_schema(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JsonSchema.objects.count(), 1)
        self.assertEqual(JsonSchema.objects.get().naam, "update")

    def test_read_schemas(self):
        schema = JsonSchemaFactory.create(naam="test", schema={})
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "naam": self.schema.naam,
                "schema": self.schema.schema,
            },
            {
                "naam": schema.naam,
                "schema": schema.schema,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_schema(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "naam": self.schema.naam,
            "schema": self.schema.schema,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_schema(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(JsonSchema.objects.count(), 0)
