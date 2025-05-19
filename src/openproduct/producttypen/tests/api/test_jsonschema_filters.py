from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status

from openproduct.producttypen.tests.factories import JsonSchemaFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestJsonSchemaFilters(BaseApiTestCase):
    path = reverse_lazy("schema-list")

    def test_naam_filter(self):
        JsonSchemaFactory.create(naam="schema a", schema={})
        JsonSchemaFactory.create(naam="schema b", schema={})

        response = self.client.get(self.path, {"naam": "schema b"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[_("aantal")], 1)
        self.assertEqual(response.data[_("resultaten")][0]["naam"], "schema b")

    def test_naam_contains_filter(self):
        JsonSchemaFactory.create(naam="schema a", schema={})
        JsonSchemaFactory.create(naam="schema b", schema={})

        response = self.client.get(self.path, {"naam__contains": "b"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[_("aantal")], 1)
        self.assertEqual(response.data[_("resultaten")][0]["naam"], "schema b")
