import uuid

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openproduct.producttypen.models import FacetType
from openproduct.producttypen.models.enums import DoelgroepChoices
from openproduct.producttypen.models.producttype import ProductType
from openproduct.producttypen.tests.factories import (
    FacetTypeFactory,
    ProductTypeFactory,
    ThemaFactory,
    UniformeProductNaamFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


class TestFacetTypeViewSet(BaseApiTestCase):
    is_superuser = True
    list_url = reverse_lazy("facet_type-list")

    def setUp(self):
        super().setUp()

    def test_read_facettype_without_credentials_returns_error(self):
        response = APIClient().get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(FacetType.objects.exists())

        FacetTypeFactory.create()
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(FacetType.objects.all().count(), 1)

        facet_type = FacetType.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uuid": str(facet_type.uuid),
                        "naam": facet_type.naam,
                        "omschrijving": facet_type.omschrijving,
                        "facetteerbaar": facet_type.facetteerbaar,
                        "meervoudig_toegestaan": facet_type.meervoudig_toegestaan,
                        "verplicht": facet_type.verplicht,
                        "waarden": [],
                    }
                ],
            },
        )

        FacetTypeFactory.create_batch(4)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertEqual(FacetType.objects.all().count(), 5)

    def test_detail(self):
        facet_type = FacetTypeFactory.create(waarden=1)
        detail_url = reverse_lazy(
            "facet_type-detail", kwargs={"uuid": str(facet_type.uuid)}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FacetType.objects.all().count(), 1)
        self.assertEqual(
            response.json(),
            {
                "uuid": str(facet_type.uuid),
                "naam": facet_type.naam,
                "omschrijving": facet_type.omschrijving,
                "facetteerbaar": facet_type.facetteerbaar,
                "meervoudig_toegestaan": facet_type.meervoudig_toegestaan,
                "verplicht": facet_type.verplicht,
                "waarden": [
                    {
                        "uuid": str(facet_type.waarden.first().uuid),
                        "naam": facet_type.waarden.first().naam,
                        "omschrijving": facet_type.waarden.first().omschrijving,
                        "actief": facet_type.waarden.first().actief,
                    }
                ],
            },
        )

    def test_read_facetten_from_producttype(self):
        facet_type = FacetTypeFactory.create(waarden=1)
        facet_waarde = facet_type.waarden.first()
        producttype = ProductTypeFactory.create()
        producttype.facetten.add(facet_waarde)
        producttype.save()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()["facetten"]), 1)
        self.assertEqual(
            response.json()["facetten"],
            [
                {
                    "uuid": str(facet_waarde.uuid),
                    "naam": facet_waarde.naam,
                    "omschrijving": facet_waarde.omschrijving,
                    "actief": facet_waarde.actief,
                    "facet_type": {
                        "uuid": str(facet_waarde.facet_type.uuid),
                        "naam": facet_waarde.facet_type.naam,
                        "omschrijving": facet_waarde.facet_type.omschrijving,
                        "facetteerbaar": facet_waarde.facet_type.facetteerbaar,
                        "meervoudig_toegestaan": facet_waarde.facet_type.meervoudig_toegestaan,
                        "verplicht": facet_waarde.facet_type.verplicht,
                    },
                }
            ],
        )

    def test_filter(self):
        facet_type = FacetTypeFactory.create(
            naam="test_a",
            facetteerbaar=True,
            meervoudig_toegestaan=True,
            verplicht=True,
            waarden=1,
        )
        FacetTypeFactory.create(
            naam="test_b",
            facetteerbaar=True,
            meervoudig_toegestaan=True,
            verplicht=False,
            waarden=1,
        )
        FacetTypeFactory.create(
            naam="test_c",
            facetteerbaar=False,
            meervoudig_toegestaan=True,
            verplicht=False,
            waarden=1,
        )

        with self.subTest("facetteerbaar"):
            response = self.client.get(self.list_url, {"facetteerbaar": True})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 2)

        with self.subTest("meervoudig_toegestaan"):
            response = self.client.get(self.list_url, {"meervoudig_toegestaan": True})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 3)

        with self.subTest("verplicht"):
            response = self.client.get(self.list_url, {"verplicht": True})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 1)

        with self.subTest("uuid"):
            response = self.client.get(self.list_url, {"uuid": str(facet_type.uuid)})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 1)
            self.assertEqual(
                response.json()["results"][0]["uuid"], str(facet_type.uuid)
            )
            # random uuid
            response = self.client.get(self.list_url, {"uuid": str(uuid.uuid4())})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 0)

        with self.subTest("naam__iexact"):
            response = self.client.get(self.list_url, {"naam__iexact": "test_a"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 1)
            self.assertEqual(
                response.json()["results"][0]["uuid"], str(facet_type.uuid)
            )
            # random name
            response = self.client.get(self.list_url, {"naam__iexact": "test_test"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 0)

        with self.subTest("waarden__uuid"):
            response = self.client.get(
                self.list_url, {"waarden__uuid": str(facet_type.waarden.first().uuid)}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 1)
            self.assertEqual(
                response.json()["results"][0]["uuid"], str(facet_type.uuid)
            )

        with self.subTest("waarden__naam"):
            response = self.client.get(
                self.list_url, {"waarden__naam": str(facet_type.waarden.first().naam)}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 1)
            self.assertEqual(
                response.json()["results"][0]["naam"], str(facet_type.naam)
            )

        with self.subTest("waarden__actief"):
            waarden = facet_type.waarden.first()
            waarden.actief = False
            waarden.save()
            response = self.client.get(self.list_url, {"waarden__actief": False})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), 1)
            self.assertEqual(
                response.json()["results"][0]["uuid"], str(facet_type.uuid)
            )


class TestProductTypeFacettenViewSet(BaseApiTestCase):
    is_superuser = True
    list_url = reverse_lazy("facet_type-list")

    def test_read_producttype_with_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=3)
        facet_waarde = facet_type.waarden.first()
        producttype = ProductTypeFactory.create()
        producttype.facetten.add(facet_waarde.pk)
        producttype.save()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["facetten"],
            [
                {
                    "uuid": str(facet_waarde.uuid),
                    "naam": facet_waarde.naam,
                    "omschrijving": facet_waarde.omschrijving,
                    "actief": facet_waarde.actief,
                    "facet_type": {
                        "uuid": str(facet_type.uuid),
                        "naam": facet_type.naam,
                        "omschrijving": facet_type.omschrijving,
                        "facetteerbaar": facet_type.facetteerbaar,
                        "meervoudig_toegestaan": facet_type.meervoudig_toegestaan,
                        "verplicht": facet_type.verplicht,
                    },
                }
            ],
        )

    def test_create_producttype_with_facetten(self):
        list_url = reverse_lazy("producttype-list")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 0)

        # create 3, but add only one
        facet_type = FacetTypeFactory.create(waarden=3)
        facet_waarde = facet_type.waarden.first()
        data = {
            "naam": "test-producttype",
            "samenvatting": "test",
            "uniforme_product_naam": UniformeProductNaamFactory.create().naam,
            "doelgroep": DoelgroepChoices.BURGERS,
            "thema_uuids": [ThemaFactory().uuid],
        }

        with self.subTest("empty list"):
            data["facetten_uuids"] = []
            data["code"] = "PT-11111"
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json()["facetten"], [])

        with self.subTest("none value"):
            data["facetten_uuids"] = None
            data["code"] = "PT-22222"
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetten_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetten_uuids",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )

        with self.subTest("one value"):
            data["facetten_uuids"] = [facet_waarde.uuid]
            data["code"] = "PT-33333"
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["facetten"],
                [
                    {
                        "uuid": str(facet_waarde.uuid),
                        "naam": facet_waarde.naam,
                        "omschrijving": facet_waarde.omschrijving,
                        "actief": facet_waarde.actief,
                        "facet_type": {
                            "uuid": str(facet_waarde.facet_type.uuid),
                            "naam": facet_waarde.facet_type.naam,
                            "omschrijving": facet_waarde.facet_type.omschrijving,
                            "facetteerbaar": facet_waarde.facet_type.facetteerbaar,
                            "meervoudig_toegestaan": facet_waarde.facet_type.meervoudig_toegestaan,
                            "verplicht": facet_waarde.facet_type.verplicht,
                        },
                    }
                ],
            )

    def test_update_producttype_with_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=3)
        facet_waarde = facet_type.waarden.first()
        producttype = ProductTypeFactory.create()
        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        data = {}

        with self.subTest("empty list"):
            data["facetten_uuids"] = []
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["facetten"], [])

        with self.subTest("none value"):
            data["facetten_uuids"] = None
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetten_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetten_uuids",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )

        with self.subTest("one value"):
            data["facetten_uuids"] = [facet_waarde.uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["facetten"],
                [
                    {
                        "uuid": str(facet_waarde.uuid),
                        "naam": facet_waarde.naam,
                        "omschrijving": facet_waarde.omschrijving,
                        "actief": facet_waarde.actief,
                        "facet_type": {
                            "uuid": str(facet_waarde.facet_type.uuid),
                            "naam": facet_waarde.facet_type.naam,
                            "omschrijving": facet_waarde.facet_type.omschrijving,
                            "facetteerbaar": facet_waarde.facet_type.facetteerbaar,
                            "meervoudig_toegestaan": facet_waarde.facet_type.meervoudig_toegestaan,
                            "verplicht": facet_waarde.facet_type.verplicht,
                        },
                    }
                ],
            )

        facet_type.meervoudig_toegestaan = True
        facet_type.save()
        with self.subTest("multiple values"):
            # PATCH
            data["facetten_uuids"] = [
                facet_waarde.uuid for facet_waarde in facet_type.waarden.all()
            ]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetten"]), 3)

    def test_validate_verplicht_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=2, verplicht=False)

        producttype = ProductTypeFactory.create()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        data = {}

        with self.subTest("not required"):
            data["facetten_uuids"] = []
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["facetten"], [])

        with self.subTest("one value"):
            data["facetten_uuids"] = [facet_type.waarden.first().uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetten"]), 1)

        # create new one
        facet_type = FacetTypeFactory.create(waarden=2, verplicht=True)

        with self.subTest("empty patch"):
            data["facetten_uuids"] = []
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetten_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetten_uuids",
                    "code": "invalid",
                    "reason": f"Verplichte facettypes ontbreken: {facet_type.naam}.",
                },
            )

        with self.subTest("one value"):
            data["facetten_uuids"] = [facet_type.waarden.first().uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetten"]), 1)

    def test_validate_meervoudig_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=2, meervoudig_toegestaan=False)

        producttype = ProductTypeFactory.create()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        data = {}

        with self.subTest("one value"):
            data["facetten_uuids"] = [facet_type.waarden.first().uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetten"]), 1)

        with self.subTest("multiple values"):
            data["facetten_uuids"] = [
                facet_waarde.uuid for facet_waarde in facet_type.waarden.all()
            ]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetten_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetten_uuids",
                    "code": "invalid",
                    "reason": f"Facettype '{facet_type.naam}' staat maar één waarde toe, gekregen: {', '.join(w.naam for w in facet_type.waarden.all())}.",
                },
            )

        # now allow multiple values
        facet_type.meervoudig_toegestaan = True
        facet_type.save()

        data["facetten_uuids"] = [
            facet_waarde.uuid for facet_waarde in facet_type.waarden.all()
        ]
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["facetten"]), 2)
