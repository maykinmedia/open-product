import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from openproduct.producttypen.tests.factories import (
    JsonSchemaFactory,
    ProductTypeFactory,
)

from ...producttypen.models.producttype import ProductStateChoices
from ..admin.product import ProductAdminForm, get_status_choices
from .factories import ProductFactory


class TestProductAdminForm(TestCase):
    def setUp(self):
        self.data = {"status"}

    def test_status_and_dates_are_not_validated_when_not_changed(self):
        data = {
            "product_type": ProductTypeFactory.create(toegestane_statussen=[]),
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()

    @patch("openproduct.producten.admin.product.validate_product_status")
    @patch("openproduct.producten.admin.product.validate_product_start_datum")
    @patch("openproduct.producten.admin.product.validate_product_eind_datum")
    def test_status_and_dates_are_validated_when_changed(
        self,
        mock_validate_product_status,
        mock_validate_product_start_datum,
        mock_validate_product_eind_datum,
    ):
        data = {
            "product_type": ProductTypeFactory.create(toegestane_statussen=["gereed"]),
            "status": "initeel",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "frequentie": "eenmalig",
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        data["status"] = "gereed"
        data["start_datum"] = datetime.date(2025, 11, 30)
        data["eind_datum"] = datetime.date(2026, 11, 30)
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()
        mock_validate_product_status.assert_called_once()
        mock_validate_product_start_datum.assert_called_once()
        mock_validate_product_eind_datum.assert_called_once()

    @patch("openproduct.producten.admin.product.validate_product_status")
    @patch("openproduct.producten.admin.product.validate_product_start_datum")
    @patch("openproduct.producten.admin.product.validate_product_eind_datum")
    def test_status__and_dates_are_validated_when_product_type_is_changed(
        self,
        mock_validate_product_status,
        mock_validate_product_start_datum,
        mock_validate_product_eind_datum,
    ):
        data = {
            "product_type": ProductTypeFactory.create(toegestane_statussen=["gereed"]),
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "frequentie": "eenmalig",
        }

        product = ProductFactory.create(**data)
        data["product_type"] = ProductTypeFactory.create(toegestane_statussen=[]).id
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()
        mock_validate_product_status.assert_called_once()
        mock_validate_product_start_datum.assert_called_once()
        mock_validate_product_eind_datum.assert_called_once()

    def test_get_status_choices_with_instance(self):
        product_type = ProductTypeFactory.create(toegestane_statussen=["actief"])
        product = ProductFactory(product_type=product_type, status="gereed")
        choices = get_status_choices(None, product)

        self.assertCountEqual(
            choices,
            [("actief", "Actief"), ("initieel", "Initieel"), ("gereed", "Gereed")],
        )

    def test_get_status_choices_with_product_type_id(self):
        product_type = ProductTypeFactory.create(toegestane_statussen=["actief"])
        choices = get_status_choices(product_type.id, None)

        self.assertCountEqual(choices, [("actief", "Actief"), ("initieel", "Initieel")])

    def test_get_status_choices_with_on_create(self):
        choices = get_status_choices(None, None)

        self.assertEqual(choices, ProductStateChoices.choices)

    def test_valid_verbruiksobject(self):
        data = {
            "product_type": ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "verbruiksobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_invalid_verbruiksobject(self):
        data = {
            "product_type": ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "verbruiksobject": {"test": "test"},
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(
            form.errors,
            {
                "verbruiksobject": [
                    _(
                        "Het verbruiksobject komt niet overeen met het schema gedefinieerd op het product type."
                    )
                ]
            },
        )

    def test_verbruiksobject_without_schema(self):
        data = {
            "product_type": ProductTypeFactory.create(),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "verbruiksobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_verbruiksobject_with_schema_without_object(self):
        data = {
            "product_type": ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
        }
        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_valid_dataobject(self):
        data = {
            "product_type": ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "dataobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_invalid_dataobject(self):
        data = {
            "product_type": ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "dataobject": {"test": "test"},
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(
            form.errors,
            {
                "dataobject": [
                    _(
                        "Het dataobject komt niet overeen met het schema gedefinieerd op het product type."
                    )
                ]
            },
        )

    def test_dataobject_without_schema(self):
        data = {
            "product_type": ProductTypeFactory.create(),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "dataobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_dataobject_with_schema_without_object(self):
        data = {
            "product_type": ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
        }
        product = ProductFactory.create(**data)
        data["product_type"] = data.pop("product_type").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})
