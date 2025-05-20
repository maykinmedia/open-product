from datetime import date
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from freezegun import freeze_time

from openproduct.producttypen.tests.factories import ProductTypeFactory

from ...producttypen.models.producttype import ProductStateChoices
from ..models.validators import (
    validate_product_eind_datum,
    validate_product_start_datum,
    validate_product_status,
)
from .factories import ProductFactory


class TestProduct(TestCase):
    def setUp(self):
        self.producttype = ProductTypeFactory.create(toegestane_statussen=["gereed"])

    def test_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        product = ProductFactory.build(
            start_datum=date(2025, 1, 12),
            eind_datum=date(2025, 1, 12),
            producttype=self.producttype,
        )

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "De eind datum van een product mag niet op een eerdere of dezelfde dag vallen als de start datum."
            ),
        ):
            product.clean()

    def test_eind_datum_is_not_allowed_to_be_before_start_datum(self):
        product = ProductFactory.build(
            start_datum=date(2025, 1, 12),
            eind_datum=date(2024, 1, 12),
            producttype=self.producttype,
        )

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "De eind datum van een product mag niet op een eerdere of dezelfde dag vallen als de start datum."
            ),
        ):
            product.clean()

    def test_start_and_eind_datum_are_allowed_to_be_null(self):
        product = ProductFactory.build(producttype=self.producttype)
        product.clean()


@freeze_time("2024-1-1")
class TestProductStateTask(TestCase):
    def setUp(self):
        self.producttype = ProductTypeFactory.create(toegestane_statussen=["actief"])

    def test_product_status_is_set_to_active_on_start_datum(self):
        product = ProductFactory.create(
            status="initieel",
            producttype=self.producttype,
            start_datum=date(2024, 1, 1),
        )

        self.assertEqual(product.status, "actief")

    def test_product_status_is_set_to_active_on_earlier_date(self):
        product = ProductFactory.create(
            status="initieel",
            producttype=self.producttype,
            start_datum=date(2023, 12, 31),
        )

        self.assertEqual(product.status, "actief")

    def test_product_status_is_not_set_to_active_on_later_date(self):
        product = ProductFactory.create(
            status="initieel",
            producttype=self.producttype,
            start_datum=date(2024, 10, 1),
        )

        self.assertEqual(product.status, "initieel")

    @patch("openproduct.producten.models.product.audit_automation_update")
    def test_product_status_is_not_set_to_active_on_later_states(
        self, mock_audit_automation_update
    ):
        for state in [
            ProductStateChoices.ACTIEF,
            ProductStateChoices.VERLOPEN,
            ProductStateChoices.GEWEIGERD,
            ProductStateChoices.INGETROKKEN,
        ]:
            with self.subTest():
                product = ProductFactory.create(
                    status=state.value,
                    producttype=self.producttype,
                    start_datum=date(2024, 1, 1),
                )
                self.assertEqual(product.status, state.value)
                mock_audit_automation_update.assert_not_called()

    def test_product_status_is_set_to_verlopen_on_eind_datum(self):
        product = ProductFactory.create(
            status="actief", producttype=self.producttype, eind_datum=date(2024, 1, 1)
        )

        self.assertEqual(product.status, "verlopen")

    def test_product_status_is_set_to_verlopen_on_earlier_date(self):
        product = ProductFactory.create(
            status="actief",
            producttype=self.producttype,
            eind_datum=date(2023, 12, 31),
        )

        self.assertEqual(product.status, "verlopen")

    def test_product_status_is_not_set_to_verlopen_on_later_date(self):
        product = ProductFactory.create(
            status="actief",
            producttype=self.producttype,
            eind_datum=date(2024, 10, 1),
        )

        self.assertEqual(product.status, "actief")

    @patch("openproduct.producten.models.product.audit_automation_update")
    def test_product_status_is_not_set_to_verlopen_on_later_states(
        self, mock_audit_automation_update
    ):
        for state in [
            ProductStateChoices.VERLOPEN,
            ProductStateChoices.GEWEIGERD,
            ProductStateChoices.INGETROKKEN,
        ]:
            with self.subTest():
                product = ProductFactory.create(
                    status=state.value,
                    producttype=self.producttype,
                    eind_datum=date(2024, 1, 1),
                )
                self.assertEqual(product.status, state.value)
                mock_audit_automation_update.assert_not_called()


class TestProductValidateMethods(TestCase):
    def test_validate_product_start_datum_raises_when_start_datum_is_set_and_actief_not_in_toegestane_statussen(
        self,
    ):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het producttype."
            ),
        ):
            validate_product_start_datum(date(2024, 1, 1), producttype)

    def test_validate_product_eind_datum_raises_when_eind_datum_is_set_and_verlopen_not_in_toegestane_statussen(
        self,
    ):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het producttype."
            ),
        ):
            validate_product_eind_datum(date(2024, 1, 1), producttype)

    def test_validate_product_status_raises_when_given_status_not_in_toegestane_statussen(
        self,
    ):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])

        with self.assertRaisesMessage(
            ValidationError,
            _("Status 'Gereed' is niet toegestaan voor het producttype {}.").format(
                producttype.naam
            ),
        ):
            validate_product_status("gereed", producttype)

    def test_validate_product_status_does_not_raise_error_on_status_initieel(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])

        validate_product_status("initieel", producttype)
