from datetime import date

from django.test import TestCase

from ..admin.producttype import ProductTypeAdminForm
from ..models import Thema
from .factories import ThemaFactory, UniformeProductNaamFactory


class TestProductTypeAdminForm(TestCase):
    def setUp(self):
        upn = UniformeProductNaamFactory.create()
        self.data = {
            "naam": "test",
            "code": "TEST-123",
            "uniforme_product_naam": upn,
            "beschrijving": "beschrijving",
            "samenvatting": "samenvatting",
            "interne_opmerkingen": "interne opmerkingen",
        }

    def test_at_least_one_thema_is_required(self):
        form = ProductTypeAdminForm(data=self.data)

        self.assertEqual(form.errors, {"themas": ["Er is minimaal één thema vereist."]})

        ThemaFactory.create()
        form = ProductTypeAdminForm(data=self.data | {"themas": Thema.objects.all()})

        self.assertEqual(form.errors, {})

    def test_publicatie_dates(self):
        ThemaFactory.create()
        data = self.data | {"themas": Thema.objects.all()}

        with self.subTest("same date"):
            form = ProductTypeAdminForm(
                data=data
                | {
                    "publicatie_start_datum": date(2025, 1, 1),
                    "publicatie_eind_datum": date(2025, 1, 1),
                }
            )
            self.assertEqual(
                form.errors,
                {
                    "__all__": [
                        "De publicatie eind datum van een producttype mag niet op een eerdere of dezelfde dag vallen als de publicate start datum."
                    ]
                },
            )

        with self.subTest("before"):
            form = ProductTypeAdminForm(
                data=data
                | {
                    "publicatie_start_datum": date(2025, 1, 1),
                    "publicatie_eind_datum": date(2024, 1, 1),
                }
            )
            self.assertEqual(
                form.errors,
                {
                    "__all__": [
                        "De publicatie eind datum van een producttype mag niet op een eerdere of dezelfde dag vallen als de publicate start datum."
                    ]
                },
            )

        with self.subTest("after"):
            form = ProductTypeAdminForm(
                data=data
                | {
                    "publicatie_start_datum": date(2025, 1, 1),
                    "publicatie_eind_datum": date(2025, 1, 10),
                }
            )
            self.assertEqual(form.errors, {})

        with self.subTest("eind datum only"):
            form = ProductTypeAdminForm(
                data=data
                | {
                    "publicatie_eind_datum": date(2025, 1, 10),
                }
            )
            self.assertEqual(
                form.errors,
                {
                    "__all__": [
                        "De publicatie eind datum kan niet zonder een publicatie start datum worden gezet."
                    ]
                },
            )

        with self.subTest("both not set"):
            form = ProductTypeAdminForm(data=data)
            self.assertEqual(form.errors, {})
