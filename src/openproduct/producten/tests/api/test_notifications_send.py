from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from freezegun import freeze_time
from notifications_api_common.models import NotificationsConfig
from rest_framework import status
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from openproduct.producten.tests.factories import ProductFactory
from openproduct.producttypen.tests.factories import ProductTypeFactory
from openproduct.utils.tests.cases import BaseApiTestCase


@freeze_time("2024-2-2T00:00:00Z")
@override_settings(NOTIFICATIONS_DISABLED=False)
class SendNotifTestCase(BaseApiTestCase):
    @classmethod
    def setUpTestData(cls):

        service, _ = Service.objects.update_or_create(
            api_root="https://notificaties-api.vng.cloud/api/v1/",
            defaults=dict(
                api_type=APITypes.nrc,
                client_id="test",
                secret="test",
                user_id="test",
                user_representation="Test",
            ),
        )
        config = NotificationsConfig.get_solo()
        config.notifications_api_service = service
        config.save()

        cls.product_type = ProductTypeFactory.create(toegestane_statussen=["gereed"])
        cls.data = {
            "product_type_id": cls.product_type.id,
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "eigenaren": [{"bsn": "111222333"}],
        }

        product = ProductFactory.create(product_type=cls.product_type)

        cls.path = reverse("product-list")
        cls.detail_path = reverse("product-detail", args=[product.id])

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_create_object(self, mock_task):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        expected_data = {
            "kanaal": "producten",
            "hoofdObject": data["url"],
            "resource": "product",
            "resourceUrl": data["url"],
            "actie": "create",
            "aanmaakdatum": "2024-02-02T01:00:00+01:00",
            "kenmerken": {
                "productType.id": data["product_type"]["id"],
                "productType.uniformeProductNaam": data["product_type"][
                    "uniforme_product_naam"
                ],
                "productType.code": data["product_type"]["code"],
            },
        }

        mock_task.assert_called_with(expected_data)

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_update_object(self, mock_task):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(self.detail_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        expected_data = {
            "kanaal": "producten",
            "hoofdObject": data["url"],
            "resource": "product",
            "resourceUrl": data["url"],
            "actie": "update",
            "aanmaakdatum": "2024-02-02T01:00:00+01:00",
            "kenmerken": {
                "productType.id": data["product_type"]["id"],
                "productType.uniformeProductNaam": data["product_type"][
                    "uniforme_product_naam"
                ],
                "productType.code": data["product_type"]["code"],
            },
        }

        mock_task.assert_called_with(expected_data)

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_partial_update_object(self, mock_task):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(self.detail_path, {"status": "initieel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        expected_data = {
            "kanaal": "producten",
            "hoofdObject": data["url"],
            "resource": "product",
            "resourceUrl": data["url"],
            "actie": "partial_update",
            "aanmaakdatum": "2024-02-02T01:00:00+01:00",
            "kenmerken": {
                "productType.id": data["product_type"]["id"],
                "productType.uniformeProductNaam": data["product_type"][
                    "uniforme_product_naam"
                ],
                "productType.code": data["product_type"]["code"],
            },
        }

        mock_task.assert_called_with(expected_data)

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_delete_object(self, mock_task):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        expected_data = {
            "kanaal": "producten",
            "hoofdObject": f"http://testserver{self.detail_path}",
            "resource": "product",
            "resourceUrl": f"http://testserver{self.detail_path}",
            "actie": "destroy",
            "aanmaakdatum": "2024-02-02T01:00:00+01:00",
            "kenmerken": {
                "productType.id": str(self.product_type.id),
                "productType.uniformeProductNaam": self.product_type.uniforme_product_naam.naam,
                "productType.code": self.product_type.code,
            },
        }

        mock_task.assert_called_with(expected_data)
