import uuid

from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openproduct.producttypen.models import FacetType, FacetWaarde
from openproduct.producttypen.models.enums import DoelgroepChoices
from openproduct.producttypen.models.producttype import ProductType
from openproduct.producttypen.tests.factories import (
    FacetTypeFactory,
    FacetWaardeFactory,
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
        producttype.facetwaarden.add(facet_waarde)
        producttype.save()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()["facetwaarden"]), 1)
        self.assertEqual(
            response.json()["facetwaarden"],
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

    def _detail_url(self, facet_type):
        return reverse_lazy("facet_type-detail", kwargs={"uuid": str(facet_type.uuid)})

    def test_create_facettype(self):
        data = {
            "naam": "doelgroep",
            "omschrijving": "omschrijving",
            "facetteerbaar": True,
            "meervoudig_toegestaan": True,
            "verplicht": False,
            "waarden": [
                {"naam": "inwoners"},
                {"naam": "bedrijven", "omschrijving": "b", "actief": False},
            ],
        }

        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        facet_type = FacetType.objects.get()
        self.assertEqual(facet_type.naam, "doelgroep")
        self.assertTrue(facet_type.facetteerbaar)
        self.assertTrue(facet_type.meervoudig_toegestaan)
        self.assertEqual(
            list(facet_type.waarden.values_list("naam", "omschrijving", "actief")),
            [("bedrijven", "b", False), ("inwoners", "", True)],
        )

    def test_create_facettype_without_waarden(self):
        response = self.client.post(self.list_url, {"naam": "doelgroep"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["waarden"], [])
        self.assertFalse(FacetWaarde.objects.exists())

    def test_create_facettype_ignores_waarde_uuid(self):
        waarde_uuid = uuid.uuid4()
        data = {"naam": "doelgroep", "waarden": [{"uuid": waarde_uuid, "naam": "a"}]}

        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(FacetWaarde.objects.get().uuid, waarde_uuid)

    def test_update_facettype(self):
        facet_type = FacetTypeFactory.create(waarden=3)
        kept, updated, removed = facet_type.waarden.all()

        data = {
            "naam": "nieuw",
            "waarden": [
                {"uuid": kept.uuid, "naam": kept.naam},
                {"uuid": updated.uuid, "naam": "aangepast"},
                {"naam": "toegevoegd"},
            ],
        }

        response = self.client.put(self._detail_url(facet_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        facet_type.refresh_from_db()
        self.assertEqual(facet_type.naam, "nieuw")
        self.assertEqual(facet_type.waarden.count(), 3)
        self.assertFalse(FacetWaarde.objects.filter(pk=removed.pk).exists())
        updated.refresh_from_db()
        self.assertEqual(updated.naam, "aangepast")
        self.assertTrue(facet_type.waarden.filter(naam="toegevoegd").exists())

    def test_update_facettype_removing_all_waarden(self):
        facet_type = FacetTypeFactory.create(waarden=2)

        response = self.client.put(
            self._detail_url(facet_type), {"naam": "nieuw", "waarden": []}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(facet_type.waarden.exists())

    def test_partial_update_facettype_without_waarden_keeps_waarden(self):
        facet_type = FacetTypeFactory.create(waarden=2)

        response = self.client.patch(self._detail_url(facet_type), {"verplicht": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        facet_type.refresh_from_db()
        self.assertTrue(facet_type.verplicht)
        self.assertEqual(facet_type.waarden.count(), 2)

    def test_update_facettype_with_waarde_of_other_facettype_returns_error(self):
        facet_type = FacetTypeFactory.create()
        waarde = FacetWaardeFactory.create()

        response = self.client.patch(
            self._detail_url(facet_type),
            {"waarden": [{"uuid": waarde.uuid, "naam": "a"}]},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "waarden")
        self.assertEqual(
            error["reason"],
            _(
                "facetwaarde uuid {} op index 0 is niet onderdeel van het facettype object."
            ).format(waarde.uuid),
        )
        waarde.refresh_from_db()
        self.assertNotEqual(waarde.facet_type, facet_type)

    def test_update_facettype_with_unknown_waarde_uuid_returns_error(self):
        facet_type = FacetTypeFactory.create()

        response = self.client.patch(
            self._detail_url(facet_type),
            {"waarden": [{"uuid": uuid.uuid4(), "naam": "a"}]},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_validation_errors(response, "waarden"))

    def test_disable_meervoudig_toegestaan(self):
        facet_type = FacetTypeFactory.create(waarden=2, meervoudig_toegestaan=True)
        producttype = ProductTypeFactory.create()

        with self.subTest("producttype has one waarde"):
            producttype.facetwaarden.set([facet_type.waarden.first()])

            response = self.client.patch(
                self._detail_url(facet_type), {"meervoudig_toegestaan": False}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            facet_type.meervoudig_toegestaan = True
            facet_type.save()

        with self.subTest("producttype has multiple waarden"):
            producttype.facetwaarden.set(facet_type.waarden.all())

            response = self.client.patch(
                self._detail_url(facet_type), {"meervoudig_toegestaan": False}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "meervoudig_toegestaan")["reason"],
                _("Er zijn producttypen met meerdere waarden van dit facettype."),
            )
            facet_type.refresh_from_db()
            self.assertTrue(facet_type.meervoudig_toegestaan)

    def test_delete_facettype(self):
        facet_type = FacetTypeFactory.create(waarden=2)
        producttype = ProductTypeFactory.create()
        producttype.facetwaarden.set(facet_type.waarden.all())

        response = self.client.delete(self._detail_url(facet_type))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FacetType.objects.exists())
        self.assertFalse(FacetWaarde.objects.exists())
        self.assertFalse(producttype.facetwaarden.exists())

    def test_make_facettype_verplicht(self):
        error_message = _(
            "Alle producttypen moeten een waarde van een facettype voordat het verplicht kan worden."
        )

        with self.subTest("create without producttypen"):
            response = self.client.post(
                self.list_url, {"naam": "doelgroep", "verplicht": True}
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        with self.subTest("create with producttypen"):
            ProductTypeFactory.create()

            response = self.client.post(
                self.list_url, {"naam": "doelgroep", "verplicht": True}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "verplicht")["reason"], error_message
            )

        with self.subTest("all producttypen have a waarde"):
            ProductType.objects.all().delete()
            facet_type = FacetTypeFactory.create(waarden=1)
            ProductTypeFactory.create().facetwaarden.add(facet_type.waarden.get())

            response = self.client.patch(
                self._detail_url(facet_type), {"verplicht": True}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("not all producttypen have a waarde"):
            facet_type = FacetTypeFactory.create(waarden=1)
            ProductTypeFactory.create().facetwaarden.add(facet_type.waarden.get())
            ProductTypeFactory.create()

            response = self.client.patch(
                self._detail_url(facet_type), {"verplicht": True}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "verplicht")["reason"], error_message
            )
            facet_type.refresh_from_db()
            self.assertFalse(facet_type.verplicht)

    def test_remove_waarde_of_verplicht_facettype(self):
        facet_type = FacetTypeFactory.create(
            waarden=2, verplicht=True, meervoudig_toegestaan=True
        )
        waarde, other_waarde = facet_type.waarden.all()
        producttype = ProductTypeFactory.create()

        with self.subTest("producttype has other waarde"):
            producttype.facetwaarden.set([waarde, other_waarde])

            response = self.client.patch(
                self._detail_url(facet_type),
                {"waarden": [{"uuid": other_waarde.uuid, "naam": other_waarde.naam}]},
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(FacetWaarde.objects.filter(pk=waarde.pk).exists())

        with self.subTest("producttype has only this waarde"):
            response = self.client.patch(self._detail_url(facet_type), {"waarden": []})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "waarden")["reason"],
                _(
                    "Het facettype is verplicht en er zijn producttypen zonder andere waarde."
                ),
            )
            self.assertTrue(FacetWaarde.objects.filter(pk=other_waarde.pk).exists())

        with self.subTest("verplicht disabled in same request"):
            response = self.client.patch(
                self._detail_url(facet_type), {"verplicht": False, "waarden": []}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(facet_type.waarden.exists())


class TestProductTypeFacettenViewSet(BaseApiTestCase):
    is_superuser = True
    list_url = reverse_lazy("facet_type-list")

    def test_read_producttype_with_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=3)
        facet_waarde = facet_type.waarden.first()
        producttype = ProductTypeFactory.create()
        producttype.facetwaarden.add(facet_waarde.pk)
        producttype.save()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["facetwaarden"],
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
            data["facetwaarden_uuids"] = []
            data["code"] = "PT-11111"
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json()["facetwaarden"], [])

        with self.subTest("none value"):
            data["facetwaarden_uuids"] = None
            data["code"] = "PT-22222"
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetwaarden_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetwaarden_uuids",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )

        with self.subTest("one value"):
            data["facetwaarden_uuids"] = [facet_waarde.uuid]
            data["code"] = "PT-33333"
            response = self.client.post(list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                response.json()["facetwaarden"],
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
            data["facetwaarden_uuids"] = []
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["facetwaarden"], [])

        with self.subTest("none value"):
            data["facetwaarden_uuids"] = None
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetwaarden_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetwaarden_uuids",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )

        with self.subTest("one value"):
            data["facetwaarden_uuids"] = [facet_waarde.uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["facetwaarden"],
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
            data["facetwaarden_uuids"] = [
                facet_waarde.uuid for facet_waarde in facet_type.waarden.all()
            ]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetwaarden"]), 3)

    def test_validate_verplicht_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=2, verplicht=False)

        producttype = ProductTypeFactory.create()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        data = {}

        with self.subTest("not required"):
            data["facetwaarden_uuids"] = []
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["facetwaarden"], [])

        with self.subTest("one value"):
            data["facetwaarden_uuids"] = [facet_type.waarden.first().uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetwaarden"]), 1)

        # create new one
        facet_type = FacetTypeFactory.create(waarden=2, verplicht=True)

        with self.subTest("empty patch"):
            data["facetwaarden_uuids"] = []
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetwaarden_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetwaarden_uuids",
                    "code": "invalid",
                    "reason": f"Verplichte facettypen ontbreken: {facet_type.naam}.",
                },
            )

        with self.subTest("one value"):
            data["facetwaarden_uuids"] = [facet_type.waarden.first().uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetwaarden"]), 1)

    def test_validate_meervoudig_facetten(self):
        facet_type = FacetTypeFactory.create(waarden=2, meervoudig_toegestaan=False)

        producttype = ProductTypeFactory.create()

        detail_url = reverse_lazy("producttype-detail", args=[producttype.uuid])
        data = {}

        with self.subTest("one value"):
            data["facetwaarden_uuids"] = [facet_type.waarden.first().uuid]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["facetwaarden"]), 1)

        with self.subTest("multiple values"):
            data["facetwaarden_uuids"] = [
                facet_waarde.uuid for facet_waarde in facet_type.waarden.all()
            ]
            response = self.client.patch(detail_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "facetwaarden_uuids")
            self.assertEqual(
                error,
                {
                    "name": "facetwaarden_uuids",
                    "code": "invalid",
                    "reason": f"Facettype '{facet_type.naam}' staat maar één waarde toe, gekregen: {', '.join(w.naam for w in facet_type.waarden.all())}.",
                },
            )

        # now allow multiple values
        facet_type.meervoudig_toegestaan = True
        facet_type.save()

        data["facetwaarden_uuids"] = [
            facet_waarde.uuid for facet_waarde in facet_type.waarden.all()
        ]
        response = self.client.patch(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["facetwaarden"]), 2)
