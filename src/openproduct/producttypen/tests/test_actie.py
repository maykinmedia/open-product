from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from openproduct.producttypen.tests.factories import ActieFactory


class TestActie(TestCase):
    def test_invalid_mapping(self):
        with self.assertRaisesMessage(
            ValidationError,
            _("De mapping komt niet overeen met het schema. (zie API spec)"),
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

    def test_url(self):
        with self.subTest("nothing"):
            actie = ActieFactory.create(dmn_config=None, dmn_tabel_id="")
            with self.assertRaisesMessage(
                ValidationError, _("Een actie moet een url of een dmn tabel hebben.")
            ):
                actie.full_clean()

        with self.subTest("url and dmn"):
            actie = ActieFactory.create(direct_url="https://google.com")
            with self.assertRaisesMessage(
                ValidationError, _("Een actie moet een url of een dmn tabel hebben.")
            ):
                actie.full_clean()

        with self.subTest("dmn config only"):
            actie = ActieFactory.create(dmn_tabel_id="")
            with self.assertRaisesMessage(
                ValidationError,
                _("Een actie dmn bestaat uit een dmn_config en dmn_tabel_id."),
            ):
                actie.full_clean()

        with self.subTest("tabel id only"):
            actie = ActieFactory.create(dmn_config=None)
            with self.assertRaisesMessage(
                ValidationError,
                _("Een actie dmn bestaat uit een dmn_config en dmn_tabel_id."),
            ):
                actie.full_clean()
