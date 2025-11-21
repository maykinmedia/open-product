import datetime
from unittest.mock import MagicMock, patch

from django.test import override_settings
from django.urls import reverse

from openproduct.producten.metrics import (
    product_create_counter,
    product_delete_counter,
    product_update_counter,
)
from openproduct.producten.tests.factories import ProductFactory, ProductTypeFactory
from openproduct.urn.models import UrnMappingConfig
from openproduct.utils.tests.cases import BaseApiTestCase


@override_settings(NOTIFICATIONS_DISABLED=True, PRODUCTEN_API_MAJOR_VERSION=0)
class ProductMetricsTests(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.producttype = ProductTypeFactory.create(
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )

        UrnMappingConfig.objects.create(
            urn="maykin:abc:ztc:zaak",
            url="https://maykin.ztc.com/api/v1/zaken",
        )

        self.data = {
            "producttype_uuid": self.producttype.uuid,
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

    @patch.object(product_create_counter, "add", wraps=product_create_counter.add)
    def test_product_create_counter(self, mock_add: MagicMock):
        self.client.post(reverse("product-list"), self.data)

        mock_add.assert_called_once_with(1)

    @patch.object(product_update_counter, "add", wraps=product_update_counter.add)
    def test_product_update_counter(self, mock_add: MagicMock):
        product = ProductFactory.create(producttype=self.producttype)

        data = self.data | {
            "eigenaren": [{"kvk_nummer": "33345678"}],
            "producttype_uuid": self.producttype.uuid,
        }

        self.client.put(
            reverse("product-detail", kwargs={"uuid": str(product.uuid)}),
            data,
        )

        mock_add.assert_called_once_with(1)

    @patch.object(product_delete_counter, "add", wraps=product_delete_counter.add)
    def test_product_delete_counter(self, mock_add: MagicMock):
        product = ProductFactory.create()

        self.client.delete(
            reverse(
                "product-detail",
                kwargs={"uuid": str(product.uuid)},
            )
        )

        mock_add.assert_called_once_with(1)
