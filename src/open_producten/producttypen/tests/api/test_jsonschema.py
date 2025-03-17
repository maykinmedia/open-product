from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.producttypen.models import JsonSchema
from open_producten.producttypen.tests.factories import JsonSchemaFactory
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProductTypeSchema(BaseApiTestCase):
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
        self.assertEqual(
            response.data,
            {
                "naam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "schema": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_schema(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JsonSchema.objects.count(), 2)

        self.assertEqual(response.data, self.data)

    def test_create_invalid_schema(self):
        data = self.data | {"schema": {"type": []}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "schema": [
                    ErrorDetail(
                        string="[] is not valid under any of the given schemas",
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_schema(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JsonSchema.objects.count(), 1)
        self.assertEqual(JsonSchema.objects.first().naam, "update")

    def test_partial_update_schema(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JsonSchema.objects.count(), 1)
        self.assertEqual(JsonSchema.objects.first().naam, "update")

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
