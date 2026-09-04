import datetime
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from freezegun import freeze_time
from rest_framework import status

from openproduct.producttypen.tests.factories import (
    ProductTypeFactory,
    ThemaFactory,
)
from openproduct.urn.models import UrnMappingConfig
from openproduct.utils.tests.cases import BaseApiTestCase

from ...cloudevents import ZAAK_GEKOPPELD, ZAAK_ONTKOPPELD
from ...models import Product
from ..factories import ProductFactory

MOCK_CLOUDEVENT_ID = "3f86493e-05c5-4088-9f2e-3d82b76a1e38"


@freeze_time("2026-08-24T11:27:00Z")
@patch("notifications_api_common.tasks.send_cloudevent.delay")
@patch("notifications_api_common.cloudevents.uuid.uuid4", lambda: MOCK_CLOUDEVENT_ID)
@override_settings(NOTIFICATIONS_SOURCE="test", LOG_NOTIFICATIONS_IN_DB=False)
class TestProductCloudEvents(BaseApiTestCase):
    is_superuser = True
    maxDiff = None

    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_create_no_cloudevent(self, mock_send_cloudevent):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create(
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )
        producttype.themas.add(thema)

        UrnMappingConfig.objects.create(
            urn="urn:nld:maykin:openzaak:ztc:zaak",
            url="https://maykin.ztc.com/api/v1/zaken",
        )

        data = {
            "naam": "Test product",
            "producttype_uuid": producttype.uuid,
            "status": "initieel",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("product-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_cloudevent.assert_not_called()

    @override_settings(ENABLE_CLOUD_EVENTS=True, REQUIRE_URN_URL_MAPPING=False)
    def test_create_with_zaak_urn(self, mock_send_cloudevent):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create(
            naam="Vergunning",
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )
        producttype.themas.add(thema)

        data = {
            "naam": "Test product",
            "producttype_uuid": producttype.uuid,
            "status": "initieel",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("product-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get()
        expected_payload = {
            "id": MOCK_CLOUDEVENT_ID,
            "source": "test",
            "specversion": "1.0",
            "type": ZAAK_GEKOPPELD,
            "subject": "d42613cd-ee22-4455-808c-c19c7b8442a1",
            "time": "2026-08-24T11:27:00Z",
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "zaak": "urn:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
                "linkTo": f"http://testserver/producten/api/v1/producten/{product.uuid}",
                "label": "Vergunning instantie.",
                "linkObjectType": "product",
            },
        }
        mock_send_cloudevent.assert_called_once_with(expected_payload, None)

    @override_settings(ENABLE_CLOUD_EVENTS=True)
    def test_create_with_zaak_url(self, mock_send_cloudevent):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create(
            naam="Vergunning",
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )
        producttype.themas.add(thema)

        UrnMappingConfig.objects.create(
            urn="urn:nld:maykin:openzaak:ztc:zaak",
            url="https://maykin.ztc.com/api/v1/zaken",
        )

        data = {
            "naam": "Test product",
            "producttype_uuid": producttype.uuid,
            "status": "initieel",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("product-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get()
        expected_payload = {
            "id": MOCK_CLOUDEVENT_ID,
            "source": "test",
            "specversion": "1.0",
            "type": ZAAK_GEKOPPELD,
            "subject": "d42613cd-ee22-4455-808c-c19c7b8442a1",
            "time": "2026-08-24T11:27:00Z",
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "zaak": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                "linkTo": f"http://testserver/producten/api/v1/producten/{product.uuid}",
                "label": "Vergunning instantie.",
                "linkObjectType": "product",
            },
        }
        mock_send_cloudevent.assert_called_once_with(expected_payload, None)

    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_delete_no_cloudevent(self, mock_send_cloudevent):
        product = ProductFactory.create()

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                reverse("product-detail", args=[product.uuid])
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_send_cloudevent.assert_not_called()

    @override_settings(ENABLE_CLOUD_EVENTS=True)
    def test_delete_with_zaak_urn(self, mock_send_cloudevent):
        product = ProductFactory.create(
            aanvraag_zaak_urn="urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                reverse("product-detail", args=[product.uuid])
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        expected_payload = {
            "id": MOCK_CLOUDEVENT_ID,
            "source": "test",
            "specversion": "1.0",
            "type": ZAAK_ONTKOPPELD,
            "subject": "d42613cd-ee22-4455-808c-c19c7b8442a1",
            "time": "2026-08-24T11:27:00Z",
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "zaak": "urn:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
                "linkTo": f"http://testserver/producten/api/v1/producten/{product.uuid}",
            },
        }
        mock_send_cloudevent.assert_called_once_with(expected_payload, None)

    @override_settings(ENABLE_CLOUD_EVENTS=True)
    def test_delete_with_zaak_url(self, mock_send_cloudevent):
        product = ProductFactory.create(
            aanvraag_zaak_url="https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                reverse("product-detail", args=[product.uuid])
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        expected_payload = {
            "id": MOCK_CLOUDEVENT_ID,
            "source": "test",
            "specversion": "1.0",
            "type": ZAAK_ONTKOPPELD,
            "subject": "d42613cd-ee22-4455-808c-c19c7b8442a1",
            "time": "2026-08-24T11:27:00Z",
            "dataref": None,
            "datacontenttype": "application/json",
            "data": {
                "zaak": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                "linkTo": f"http://testserver/producten/api/v1/producten/{product.uuid}",
            },
        }
        mock_send_cloudevent.assert_called_once_with(expected_payload, None)

    @override_settings(ENABLE_CLOUD_EVENTS=False)
    def test_update_no_cloudevent(self, mock_send_cloudevent):
        product = ProductFactory.create(
            aanvraag_zaak_url="https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        data = {
            "naam": "Test product",
            "producttype_uuid": product.producttype.uuid,
            "status": "initieel",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/7f543f2c-0352-4179-89f0-105c303787d3",
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(
                reverse("product-detail", args=[product.uuid]), data=data
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_cloudevent.assert_not_called()

    @override_settings(ENABLE_CLOUD_EVENTS=True)
    def test_update_without_change_in_zaak_url(self, mock_send_cloudevent):
        product = ProductFactory.create(
            naam="Test product",
            aanvraag_zaak_url="https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

        data = {
            "naam": "Some changed name",
            "producttype_uuid": product.producttype.uuid,
            "status": "initieel",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(
                reverse("product-detail", args=[product.uuid]), data=data
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_cloudevent.assert_not_called()

    @override_settings(ENABLE_CLOUD_EVENTS=True)
    def test_update_with_change_in_zaak_url(self, mock_send_cloudevent):
        product = ProductFactory.create(
            naam="Test product",
            aanvraag_zaak_url="https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            producttype__naam="Vergunning",
        )

        data = {
            "naam": "Some changed name",
            "producttype_uuid": product.producttype.uuid,
            "status": "initieel",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/7f543f2c-0352-4179-89f0-105c303787d3",
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(
                reverse("product-detail", args=[product.uuid]), data=data
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            mock_send_cloudevent.call_args_list[0][0][0],
            {
                "id": MOCK_CLOUDEVENT_ID,
                "source": "test",
                "specversion": "1.0",
                "type": ZAAK_ONTKOPPELD,
                "subject": "d42613cd-ee22-4455-808c-c19c7b8442a1",
                "time": "2026-08-24T11:27:00Z",
                "dataref": None,
                "datacontenttype": "application/json",
                "data": {
                    "zaak": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "linkTo": f"http://testserver/producten/api/v1/producten/{product.uuid}",
                },
            },
        )
        self.assertEqual(
            mock_send_cloudevent.call_args_list[1][0][0],
            {
                "id": MOCK_CLOUDEVENT_ID,
                "source": "test",
                "specversion": "1.0",
                "type": ZAAK_GEKOPPELD,
                "subject": "7f543f2c-0352-4179-89f0-105c303787d3",
                "time": "2026-08-24T11:27:00Z",
                "dataref": None,
                "datacontenttype": "application/json",
                "data": {
                    "zaak": "https://maykin.ztc.com/api/v1/zaken/7f543f2c-0352-4179-89f0-105c303787d3",
                    "linkTo": f"http://testserver/producten/api/v1/producten/{product.uuid}",
                    "label": "Vergunning instantie.",
                    "linkObjectType": "product",
                },
            },
        )
