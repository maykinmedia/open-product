from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.producttypen.models import Thema
from openproduct.producttypen.tests.factories import ProductTypeFactory, ThemaFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestThemaViewSet(BaseApiTestCase):
    path = reverse_lazy("thema-list")

    def setUp(self):
        super().setUp()
        self.data = {
            "naam": "test-thema",
            "hoofd_thema": None,
            "producttype_uuids": [],
        }

    def detail_path(self, thema):
        return reverse("thema-detail", args=[thema.uuid])

    def test_read_thema_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "naam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "producttype_uuids": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "hoofd_thema": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_minimal_thema(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thema.objects.count(), 1)
        thema = Thema.objects.first()
        expected_data = {
            "uuid": str(thema.uuid),
            "naam": thema.naam,
            "beschrijving": thema.beschrijving,
            "gepubliceerd": False,
            "hoofd_thema": None,
            "producttypen": [],
            "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
            "update_datum": thema.update_datum.astimezone().isoformat(),
        }
        self.assertEqual(response.data, expected_data)

    def test_create_thema_with_hoofd_thema(self):
        hoofd_thema = ThemaFactory.create()
        data = self.data | {"hoofd_thema": hoofd_thema.uuid}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thema.objects.count(), 2)

        thema = Thema.objects.get(uuid=response.data["uuid"])
        self.assertEqual(thema.hoofd_thema, hoofd_thema)
        expected_data = {
            "uuid": str(thema.uuid),
            "naam": thema.naam,
            "beschrijving": thema.beschrijving,
            "gepubliceerd": False,
            "hoofd_thema": thema.hoofd_thema.uuid,
            "producttypen": [],
            "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
            "update_datum": thema.update_datum.astimezone().isoformat(),
        }
        self.assertEqual(response.data, expected_data)

    def test_create_thema_with_producttype(self):
        producttype = ProductTypeFactory.create()
        data = self.data | {"producttype_uuids": [producttype.uuid]}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thema.objects.count(), 1)
        self.assertEqual(
            list(Thema.objects.values_list("producttypen", flat=True)),
            [producttype.id],
        )

    def test_create_hoofd_thema_with_duplicate_producttypen_returns_error(self):
        producttype = ProductTypeFactory.create()
        data = self.data | {"producttype_uuids": [producttype.uuid, producttype.uuid]}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "producttype_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(
                            producttype.uuid
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_published_sub_thema_with_unpublished_hoofd_thema_returns_error(
        self,
    ):
        hoofd_thema = ThemaFactory.create(gepubliceerd=False)

        data = self.data | {"hoofd_thema": hoofd_thema.uuid, "gepubliceerd": True}

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_thema": [
                    ErrorDetail(
                        string=_(
                            "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_change_from_root_to_hoofd_thema(self):
        new_hoofd_thema = ThemaFactory.create()
        thema = ThemaFactory.create()

        data = self.data | {"hoofd_thema": new_hoofd_thema.uuid}
        response = self.client.put(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(thema.hoofd_thema, new_hoofd_thema)

    def test_update_change_from_hoofd_thema_to_root(self):
        hoofd_thema = ThemaFactory.create()
        thema = ThemaFactory.create(naam="test-thema", hoofd_thema=hoofd_thema)

        data = self.data | {"hoofd_thema": None}
        response = self.client.put(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(thema.hoofd_thema, None)

    def test_update_change_from_hoofd_thema_to_hoofd_thema(self):
        hoofd_thema = ThemaFactory.create()
        thema = ThemaFactory.create(naam="test-thema", hoofd_thema=hoofd_thema)

        new_hoofd_thema = ThemaFactory.create()

        data = self.data | {"hoofd_thema": new_hoofd_thema.uuid}
        response = self.client.put(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(thema.hoofd_thema, new_hoofd_thema)

    def test_update_hoofd_thema_with_duplicate_producttypen_returns_error(self):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create()
        data = self.data | {"producttype_uuids": [producttype.uuid, producttype.uuid]}

        response = self.client.put(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "producttype_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(
                            producttype.uuid
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_unpublished_sub_thema_to_published_with_unpublished_hoofd_thema_returns_error(
        self,
    ):
        hoofd_thema = ThemaFactory.create(gepubliceerd=False)
        sub_thema = ThemaFactory.create(naam="sub thema", hoofd_thema=hoofd_thema)

        data = self.data | {"hoofd_thema": hoofd_thema.uuid, "gepubliceerd": True}

        response = self.client.put(self.detail_path(sub_thema), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_thema": [
                    ErrorDetail(
                        string=_(
                            "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_published_hoofd_thema_to_unpublished_with_published_sub_thema_returns_error(
        self,
    ):
        hoofd_thema = ThemaFactory.create(gepubliceerd=True)
        ThemaFactory.create(
            naam="sub thema", hoofd_thema=hoofd_thema, gepubliceerd=True
        )

        data = self.data | {"hoofd_thema": None, "gepubliceerd": False}

        response = self.client.put(self.detail_path(hoofd_thema), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_thema": [
                    ErrorDetail(
                        string=_(
                            "Thema's kunnen niet ongepubliceerd worden als ze gepubliceerde sub-thema's hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update(self):
        hoofd_thema = ThemaFactory.create()
        thema = ThemaFactory.create(naam="test-thema", hoofd_thema=hoofd_thema)

        data = {"naam": "update"}
        response = self.client.patch(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(thema.naam, "update")
        self.assertEqual(thema.hoofd_thema, hoofd_thema)

    def test_partial_update_change_hoofd_thema(self):
        hoofd_thema = ThemaFactory.create()
        thema = ThemaFactory.create(naam="test-thema", hoofd_thema=hoofd_thema)

        new_hoofd_thema = ThemaFactory.create()

        data = {"hoofd_thema": new_hoofd_thema.uuid}
        response = self.client.patch(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(thema.hoofd_thema, new_hoofd_thema)

    def test_partial_update_change_hoofd_thema_to_root(self):
        hoofd_thema = ThemaFactory.create()
        thema = ThemaFactory.create(naam="test-thema", hoofd_thema=hoofd_thema)

        data = {"hoofd_thema": None}
        response = self.client.patch(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(thema.hoofd_thema, None)

    def test_partial_update_hoofd_thema_with_duplicate_producttypen_returns_error(
        self,
    ):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create()
        data = {"producttype_uuids": [producttype.uuid, producttype.uuid]}

        response = self.client.patch(self.detail_path(thema), data)

        thema.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "producttype_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(
                            producttype.uuid
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_unpublished_sub_thema_to_published_with_unpublished_hoofd_thema_returns_error(
        self,
    ):
        hoofd_thema = ThemaFactory.create(gepubliceerd=False)
        sub_thema = ThemaFactory.create(naam="sub thema", hoofd_thema=hoofd_thema)

        data = {"gepubliceerd": True}

        response = self.client.patch(self.detail_path(sub_thema), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_thema": [
                    ErrorDetail(
                        string=_(
                            "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_published_hoofd_thema_to_unpublished_with_published_sub_thema_returns_error(
        self,
    ):
        hoofd_thema = ThemaFactory.create(gepubliceerd=True)
        ThemaFactory.create(
            naam="sub thema", hoofd_thema=hoofd_thema, gepubliceerd=True
        )

        data = {"gepubliceerd": False}

        response = self.client.patch(self.detail_path(hoofd_thema), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "hoofd_thema": [
                    ErrorDetail(
                        string=_(
                            "Thema's kunnen niet ongepubliceerd worden als ze gepubliceerde sub-thema's hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_read_producttype(self):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create()
        thema.producttypen.add(producttype)
        thema.save()

        response = self.client.get(self.detail_path(thema))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "uuid": str(producttype.uuid),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": [],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
                "keywords": [],
            }
        ]

        self.assertEqual(response.data["producttypen"], expected_data)

    def test_read_themas(self):
        thema1 = ThemaFactory.create()
        thema2 = ThemaFactory.create()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[_("aantal")], 2)
        expected_data = [
            {
                "uuid": str(thema1.uuid),
                "naam": thema1.naam,
                "beschrijving": thema1.beschrijving,
                "gepubliceerd": True,
                "hoofd_thema": None,
                "producttypen": [],
                "aanmaak_datum": thema1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": thema1.update_datum.astimezone().isoformat(),
            },
            {
                "uuid": str(thema2.uuid),
                "naam": thema2.naam,
                "beschrijving": thema2.beschrijving,
                "gepubliceerd": True,
                "hoofd_thema": None,
                "producttypen": [],
                "aanmaak_datum": thema2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": thema2.update_datum.astimezone().isoformat(),
            },
        ]
        self.assertCountEqual(response.data[_("resultaten")], expected_data)

    def test_read_thema(self):
        thema = ThemaFactory.create()

        response = self.client.get(self.detail_path(thema))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "uuid": str(thema.uuid),
            "naam": thema.naam,
            "beschrijving": thema.beschrijving,
            "gepubliceerd": True,
            "hoofd_thema": None,
            "producttypen": [],
            "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
            "update_datum": thema.update_datum.astimezone().isoformat(),
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_thema(self):
        thema = ThemaFactory.create()

        response = self.client.delete(self.detail_path(thema))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Thema.objects.count(), 0)

    def test_delete_thema_when_linked_producttype_has_one_thema(self):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create(naam="test")
        producttype.themas.add(thema)
        producttype.save()

        response = self.client.delete(self.detail_path(thema))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "producttypen": [
                    "Producttype test moet aan een minimaal één thema zijn gelinkt."
                ]
            },
        )

    def test_delete_thema_when_linked_producttype_has_other_themas(self):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create(naam="test")
        producttype.themas.add(thema)
        producttype.themas.add(ThemaFactory())
        producttype.save()

        response = self.client.delete(self.detail_path(thema))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Thema.objects.count(), 1)

    def test_deleting_thema_with_sub_themas_raises_error(self):
        thema = ThemaFactory.create()
        ThemaFactory.create(hoofd_thema=thema)

        response = self.client.delete(self.detail_path(thema))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "sub_themas": [
                    "Dit thema kan niet worden verwijderd omdat er gerelateerde sub_themas zijn."
                ]
            },
        )

    def test_thema_cannot_reference_itself(self):
        thema = ThemaFactory.create()

        data = {"hoofd_thema": thema.uuid}
        response = self.client.patch(self.detail_path(thema), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"hoofd_thema": ["Een thema kan niet zijn eigen hoofd thema zijn."]},
        )
