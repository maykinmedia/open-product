from django.core.exceptions import ValidationError
from django.test import TestCase

from openproduct.producttypen.tests.factories import ActieFactory


class TestActie(TestCase):
    def test_invalid_mapping(self):
        with self.assertRaisesMessage(
            ValidationError,
            "De mapping komt niet overeen met het schema. (zie API spec)",
        ):
            actie = ActieFactory.create(mapping={"code": "abc", "test": "123"})
            actie.full_clean()

    def test_valid_mapping(self):
        actie = ActieFactory.create(
            mapping={
                "product": [
                    {"name": "status", "classType": "String", "regex": "$.status"}
                ]
            }
        )
        actie.full_clean()
