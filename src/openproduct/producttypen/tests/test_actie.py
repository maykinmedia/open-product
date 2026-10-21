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

    def test_dmn_fields(self):
        with self.subTest("DMN with config and tabel id"):
            ActieFactory(type=ActieTypeChoices.DMN).full_clean()

        with self.subTest("DMN without tabel id"):
            actie = ActieFactory(type=ActieTypeChoices.DMN, dmn_tabel_id="")

            with self.assertRaisesMessage(
                ValidationError,
                _(
                    "Dmn velden zijn alleen toegestaan (en verplicht) bij een 'dmn' actie"
                ),
            ):
                actie.full_clean()

        for type in (ActieTypeChoices.FORMULIER, ActieTypeChoices.API):
            for field, kwargs in (
                ("dmn_config", {"dmn_tabel_id": ""}),
                ("dmn_tabel_id", {"dmn_config": None}),
            ):
                with self.subTest(f"{type} with {field}"):
                    actie = ActieFactory(
                        type=type,
                        method=ActieMethodChoices.POST
                        if type == ActieTypeChoices.API
                        else "",
                        direct_url="http://example.com",
                        **kwargs,
                    )

                    with self.assertRaisesMessage(
                        ValidationError,
                        _(
                            "Dmn velden zijn alleen toegestaan (en verplicht) bij een 'dmn' actie"
                        ),
                    ):
                        actie.full_clean()
