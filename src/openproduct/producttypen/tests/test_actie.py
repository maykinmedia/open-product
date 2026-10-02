from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from openproduct.producttypen.models.enums import ActieMethodChoices, ActieTypeChoices
from openproduct.producttypen.tests.factories import ActieFactory


class TestActie(TestCase):
    def test_method(self):
        with self.subTest("API with method"):
            actie = ActieFactory(
                type=ActieTypeChoices.API,
                method=ActieMethodChoices.POST,
                direct_url="http://example.com",
                dmn_config=None,
                dmn_tabel_id="",
            )

            actie.full_clean()

        with self.subTest("API without method"):
            actie = ActieFactory(
                type=ActieTypeChoices.API, direct_url="http://example.com"
            )

            with self.assertRaisesMessage(
                ValidationError,
                _("Method is alleen toegestaan (en verplicht) bij een 'api' actie"),
            ):
                actie.full_clean()
