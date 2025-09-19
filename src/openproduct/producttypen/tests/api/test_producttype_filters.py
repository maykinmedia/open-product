from datetime import date
from uuid import uuid4

from django.urls import reverse, reverse_lazy

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from openproduct.locaties.tests.factories import (
    ContactFactory,
    LocatieFactory,
    OrganisatieFactory,
)
from openproduct.producttypen.tests.factories import (
    ContentElementFactory,
    ContentLabelFactory,
    ExterneCodeFactory,
    JsonSchemaFactory,
    ParameterFactory,
    ProcesFactory,
    ProductTypeFactory,
    ThemaFactory,
    UniformeProductNaamFactory,
    VerzoekTypeFactory,
    ZaakTypeFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


class TestProductTypeFilters(BaseApiTestCase):
    path = reverse_lazy("producttype-list")

    @freeze_time("2025-01-01")
    def test_gepubliceerd_filter(self):
        not_set = ProductTypeFactory.create()
        in_future = ProductTypeFactory.create(publicatie_start_datum=date(2026, 1, 1))
        in_past = ProductTypeFactory.create(publicatie_start_datum=date(2024, 1, 1))
        in_between = ProductTypeFactory.create(
            publicatie_start_datum=date(2024, 1, 1),
            publicatie_eind_datum=date(2025, 1, 10),
        )
        in_future_with_end = ProductTypeFactory.create(
            publicatie_start_datum=date(2026, 1, 1),
            publicatie_eind_datum=date(2027, 1, 10),
        )
        after = ProductTypeFactory.create(
            publicatie_start_datum=date(2024, 1, 1),
            publicatie_eind_datum=date(2024, 1, 10),
        )

        response = self.client.get(self.path, {"gepubliceerd": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertCountEqual(
            [pt["uuid"] for pt in response.data["results"]],
            [str(in_past.uuid), str(in_between.uuid)],
        )

        response = self.client.get(self.path, {"gepubliceerd": False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)
        self.assertCountEqual(
            [pt["uuid"] for pt in response.data["results"]],
            [
                str(not_set.uuid),
                str(in_future.uuid),
                str(in_future_with_end.uuid),
                str(after.uuid),
            ],
        )

    def test_uniforme_product_naam_filter(self):
        ProductTypeFactory.create(
            uniforme_product_naam=UniformeProductNaamFactory(naam="parkeervergunning")
        )
        ProductTypeFactory.create(
            uniforme_product_naam=UniformeProductNaamFactory(naam="aanleunwoning")
        )

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uniforme_product_naam"],
            "parkeervergunning",
        )

    def test_externe_code_filter(self):
        producttype_1 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="12345", producttype=producttype_1)

        producttype_2 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="9837549857", producttype=producttype_2)

        response = self.client.get(self.path, {"externe_code": "[ISO:12345]"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(producttype_1.uuid))

    def test_multiple_externe_code_filters(self):
        producttype_1 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="12345", producttype=producttype_1)
        ExterneCodeFactory(naam="OSI", code="456", producttype=producttype_1)

        producttype_2 = ProductTypeFactory.create()
        ExterneCodeFactory(naam="ISO", code="9837549857", producttype=producttype_2)

        response = self.client.get(
            self.path, {"externe_code": ("[ISO:12345]", "[OSI:456]")}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(producttype_1.uuid))

    def test_externe_code_filter_without_brackets(self):
        response = self.client.get(self.path, {"externe_code": "abc"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter_without_key_value(self):
        response = self.client.get(self.path, {"externe_code": "[:]"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_first_externe_code_filter_without_key_value(self):
        response = self.client.get(self.path, {"externe_code": ("[:]", "[ISO:123]")})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_externe_code_filter_with_invalid_characters(self):
        response = self.client.get(self.path, {"externe_code": "[a[b:[b:a]]"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parameter_filter(self):
        producttype_1 = ProductTypeFactory.create()
        ParameterFactory(naam="doelgroep", waarde="inwoners", producttype=producttype_1)

        producttype_2 = ProductTypeFactory.create()
        ParameterFactory(
            naam="doelgroep", waarde="bedrijven", producttype=producttype_2
        )

        response = self.client.get(self.path, {"parameter": "[doelgroep:inwoners]"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(producttype_1.uuid))

    def test_multiple_parameter_filters(self):
        producttype_1 = ProductTypeFactory.create()
        ParameterFactory(naam="doelgroep", waarde="inwoners", producttype=producttype_1)
        ParameterFactory(naam="buurt", waarde="kwartier", producttype=producttype_1)

        producttype_2 = ProductTypeFactory.create()
        ParameterFactory(
            naam="doelgroep", waarde="bedrijven", producttype=producttype_2
        )

        response = self.client.get(
            self.path, {"parameter": ("[doelgroep:inwoners]", "[buurt:kwartier]")}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(producttype_1.uuid))

    def test_parameter_filter_without_brackets(self):
        response = self.client.get(self.path, {"parameter": "abc"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parameter_filter_without_key_value(self):
        response = self.client.get(self.path, {"parameter": "[:]"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_first_parameter_filter_without_key_value(self):
        response = self.client.get(
            self.path, {"parameter": ("[:]", "[doelgroep:inwoners]")}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parameter_filter_with_invalid_characters(self):
        response = self.client.get(self.path, {"parameter": "[a[b:[b:a]]"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_producttype_code_filter(self):
        ProductTypeFactory.create(code="123")
        ProductTypeFactory.create(code="8234098q2730492873")

        response = self.client.get(self.path, {"code": "8234098q2730492873"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["code"], "8234098q2730492873")

    def test_letter_filter(self):
        producttype_1 = ProductTypeFactory.create(naam="Parkeervergunning")
        producttype_2 = ProductTypeFactory.create(naam="Aanbouw")

        with self.subTest("NL"):
            response = self.client.get(
                self.path, {"letter": "P"}, headers={"Accept-Language": "nl"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["naam"], "Parkeervergunning")

        with self.subTest("EN"):
            producttype_1.set_current_language("en")
            producttype_1.naam = "ssss"
            producttype_1.save()

            producttype_2.set_current_language("en")
            producttype_2.naam = "qqqq"
            producttype_2.save()

            response = self.client.get(
                self.path, {"letter": "A"}, headers={"Accept-Language": "en"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["naam"], "qqqq")

    def test_producttype_naam_filter(self):
        uuid = uuid4()
        ProductTypeFactory.create(naam="parkeervergunning", uuid=uuid)
        ProductTypeFactory.create(naam="aanbouw")

        response = self.client.get(self.path, {"naam": "parkeervergunning"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(uuid))

    def test_producttype_content_label_filter(self):
        producttype = ProductTypeFactory.create()
        element_1 = ContentElementFactory.create(producttype=producttype)
        element_1.labels.add(ContentLabelFactory.create(naam="openingstijden"))
        element_1.labels.add(ContentLabelFactory.create(naam="main"))

        element_2 = ContentElementFactory.create(producttype=producttype)
        element_2.labels.add(ContentLabelFactory.create(naam="stappenplan"))

        path = reverse("producttype-content", args=(producttype.uuid,))

        with self.subTest("single label filter"):
            response = self.client.get(path, {"labels": "openingstijden"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["labels"], ["main", "openingstijden"])

        with self.subTest("multiple labels same content"):
            response = self.client.get(path, {"labels": "openingstijden,main"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["labels"], ["main", "openingstijden"])

        with self.subTest("multiple labels different content"):
            response = self.client.get(path, {"labels": "openingstijden,stappenplan"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)

        with self.subTest("non existing label"):
            response = self.client.get(path, {"labels": "test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 0)

    def test_producttype_content_exclude_label_filter(self):
        producttype = ProductTypeFactory.create()
        element_1 = ContentElementFactory.create(producttype=producttype)
        element_1.labels.add(ContentLabelFactory.create(naam="openingstijden"))
        element_1.labels.add(ContentLabelFactory.create(naam="main"))

        element_2 = ContentElementFactory.create(producttype=producttype)
        element_2.labels.add(ContentLabelFactory.create(naam="stappenplan"))

        path = reverse("producttype-content", args=(producttype.uuid,))

        with self.subTest("single label filter"):
            response = self.client.get(path, {"exclude_labels": "openingstijden"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["labels"], ["stappenplan"])

        with self.subTest("multiple labels same content"):
            response = self.client.get(path, {"exclude_labels": "openingstijden,main"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["labels"], ["stappenplan"])

        with self.subTest("multiple labels different content"):
            response = self.client.get(
                path, {"exclude_labels": "openingstijden,stappenplan"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 0)

        with self.subTest("non existing label"):
            response = self.client.get(path, {"exclude_labels": "test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)

    def test_aanmaak_datum_filter(self):
        with freeze_time("2024-06-07"):
            ProductTypeFactory.create()
        with freeze_time("2025-06-07"):
            ProductTypeFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"aanmaak_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["aanmaak_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"aanmaak_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["aanmaak_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"aanmaak_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["aanmaak_datum"],
                "2025-06-07T02:00:00+02:00",
            )

    def test_update_datum_filter(self):
        with freeze_time("2024-06-07"):
            ProductTypeFactory.create()
        with freeze_time("2025-06-07"):
            ProductTypeFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"update_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["update_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"update_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["update_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"update_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["update_datum"],
                "2025-06-07T02:00:00+02:00",
            )

    def test_publicatie_start_datum_filter(self):
        ProductTypeFactory.create(publicatie_start_datum=date(2024, 6, 7))
        ProductTypeFactory.create(publicatie_start_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"publicatie_start_datum": "2024-06-07"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["publicatie_start_datum"], "2024-06-07"
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.path, {"publicatie_start_datum__lte": "2024-07-07"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["publicatie_start_datum"], "2024-06-07"
            )

        with self.subTest("gte"):
            response = self.client.get(
                self.path, {"publicatie_start_datum__gte": "2025-04-07"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["publicatie_start_datum"], "2025-06-07"
            )

    def test_publicatie_eind_datum_filter(self):
        ProductTypeFactory.create(publicatie_eind_datum=date(2024, 6, 7))
        ProductTypeFactory.create(publicatie_eind_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"publicatie_eind_datum": "2024-06-07"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["publicatie_eind_datum"], "2024-06-07"
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.path, {"publicatie_eind_datum__lte": "2024-07-07"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["publicatie_eind_datum"], "2024-06-07"
            )

        with self.subTest("gte"):
            response = self.client.get(
                self.path, {"publicatie_eind_datum__gte": "2025-04-07"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["publicatie_eind_datum"], "2025-06-07"
            )

    def test_keywords_filter(self):
        ProductTypeFactory.create(keywords=["test", "wonen", "jongeren"])
        ProductTypeFactory.create(
            keywords=[
                "test",
                "ouderen",
            ]
        )

        with self.subTest("single keyword"):
            response = self.client.get(self.path, {"keywords": "wonen"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["keywords"],
                ["test", "wonen", "jongeren"],
            )

        with self.subTest("multiple keywords same producttype"):
            response = self.client.get(self.path, {"keywords": "wonen,jongeren"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["keywords"],
                ["test", "wonen", "jongeren"],
            )

        with self.subTest("multiple keywords different producttypes"):
            response = self.client.get(self.path, {"keywords": "jongeren,ouderen"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("overlap"):
            response = self.client.get(self.path, {"keywords": "test,jongeren,ouderen"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("duplicate keywords single producttype"):
            response = self.client.get(self.path, {"keywords": "test,test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("duplicate keywords single producttype"):
            response = self.client.get(self.path, {"keywords": "jongeren,jongeren"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["keywords"],
                ["test", "wonen", "jongeren"],
            )

        with self.subTest("non existing keyword"):
            response = self.client.get(self.path, {"keywords": "abc"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 0)

    def test_toegestane_statussen_filter(self):
        ProductTypeFactory.create(toegestane_statussen=["actief", "gereed", "verlopen"])
        ProductTypeFactory.create(
            toegestane_statussen=[
                "gereed",
                "geweigerd",
            ]
        )

        with self.subTest("single status"):
            response = self.client.get(self.path, {"toegestane_statussen": "actief"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("multiple statuses same content"):
            response = self.client.get(
                self.path, {"toegestane_statussen": "actief,verlopen"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["toegestane_statussen"],
                ["actief", "gereed", "verlopen"],
            )

        with self.subTest("multiple statuses different producttypes"):
            response = self.client.get(
                self.path, {"toegestane_statussen": "actief,geweigerd"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("overlap"):
            response = self.client.get(
                self.path, {"toegestane_statussen": "actief,gereed,geweigerd"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("duplicate status multiple producttypes"):
            response = self.client.get(
                self.path, {"toegestane_statussen": "gereed,gereed"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("duplicate status single producttype"):
            response = self.client.get(
                self.path, {"toegestane_statussen": "actief,actief"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["toegestane_statussen"],
                ["actief", "gereed", "verlopen"],
            )

        with self.subTest("non existing status"):
            response = self.client.get(self.path, {"toegestane_statussen": "abc"})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data,
                {
                    "toegestane_statussen": [
                        ErrorDetail(
                            string="Selecteer een geldige keuze. abc is geen beschikbare keuze.",
                            code="invalid_choice",
                        )
                    ]
                },
            )

    def test_verbruiksobject_schema_filter(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}},
            "required": ["naam"],
        }
        ProductTypeFactory.create(
            verbruiksobject_schema=JsonSchemaFactory(naam="test-schema", schema=schema)
        )
        ProductTypeFactory.create(
            verbruiksobject_schema=JsonSchemaFactory(
                naam="parkeer-verbruik-schema", schema=schema
            )
        )

        response = self.client.get(
            self.path, {"verbruiksobject_schema__naam": "parkeer-verbruik-schema"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["verbruiksobject_schema"]["naam"],
            "parkeer-verbruik-schema",
        )

    def test_zaaktype_uuid_filter(self):
        uuid = uuid4()

        ZaakTypeFactory.create(uuid=uuid)
        ZaakTypeFactory.create()

        response = self.client.get(self.path, {"zaaktypen__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertIn(str(uuid), response.data["results"][0]["zaaktypen"][0]["url"])

    def test_verzoektype_uuid_filter(self):
        uuid = uuid4()

        VerzoekTypeFactory.create(uuid=uuid)
        VerzoekTypeFactory.create()

        response = self.client.get(self.path, {"verzoektypen__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertIn(str(uuid), response.data["results"][0]["verzoektypen"][0]["url"])

    def test_proces_uuid_filter(self):
        uuid = uuid4()

        ProcesFactory.create(uuid=uuid)
        ProcesFactory.create()

        response = self.client.get(self.path, {"processen__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertIn(str(uuid), response.data["results"][0]["processen"][0]["url"])

    def test_thema_naam_filter(self):
        producttype = ProductTypeFactory.create()
        producttype.themas.add(ThemaFactory.create(naam="thema"))
        producttype.save()

        producttype_2 = ProductTypeFactory.create()
        producttype_2.themas.add(ThemaFactory.create(naam="test"))
        producttype_2.save()

        with self.subTest("exact"):
            response = self.client.get(self.path, {"themas__naam": "thema"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("thema", response.data["results"][0]["themas"][0]["naam"])

        with self.subTest("in"):
            producttype.themas.add(ThemaFactory.create(naam="abc"))
            producttype.save()

            response = self.client.get(self.path, {"themas__naam__in": "thema,abc"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertCountEqual(
                ["thema", "abc"],
                [response.data["results"][0]["themas"][i]["naam"] for i in range(2)],
            )

        with self.subTest("distinct"):
            producttype.themas.add(ThemaFactory.create(naam="thema"))

            response = self.client.get(self.path, {"themas__naam": "thema"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_thema_uuid_filter(self):
        uuid = uuid4()

        producttype = ProductTypeFactory.create()
        producttype.themas.add(ThemaFactory.create(uuid=uuid))
        producttype.save()

        producttype_2 = ProductTypeFactory.create()
        producttype_2.themas.add(ThemaFactory.create())
        producttype_2.save()

        with self.subTest("exact"):
            response = self.client.get(self.path, {"themas__uuid": uuid})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(str(uuid), response.data["results"][0]["themas"][0]["uuid"])

        with self.subTest("in"):
            uuid_2 = uuid4()
            producttype.themas.add(ThemaFactory.create(uuid=uuid_2))
            producttype.save()

            response = self.client.get(
                self.path, {"themas__uuid__in": f"{uuid},{uuid_2}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertCountEqual(
                [str(uuid), str(uuid_2)],
                [response.data["results"][0]["themas"][i]["uuid"] for i in range(2)],
            )

    def test_contact_uuid_filter(self):
        uuid = uuid4()

        producttype = ProductTypeFactory.create()
        producttype.contacten.add(ContactFactory.create(uuid=uuid))

        uuid_2 = uuid4()
        producttype_2 = ProductTypeFactory.create()
        producttype_2.contacten.add(ContactFactory.create(uuid=uuid_2))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"contacten__uuid": uuid})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(
                str(uuid), response.data["results"][0]["contacten"][0]["uuid"]
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"contacten__uuid__in": f"{uuid},{uuid_2}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("distinct"):
            uuid_3 = uuid4()
            producttype.contacten.add(ContactFactory.create(uuid=uuid_3))

            response = self.client.get(
                self.path, {"contacten__uuid__in": f"{uuid},{uuid_3}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_contact_naam_filter(self):
        producttype = ProductTypeFactory.create()
        producttype.contacten.add(ContactFactory.create(naam="test"))

        producttype_2 = ProductTypeFactory.create()
        producttype_2.contacten.add(ContactFactory.create(naam="123"))

        with self.subTest("contains"):
            response = self.client.get(self.path, {"contacten__naam__contains": "test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("test", response.data["results"][0]["contacten"][0]["naam"])

        with self.subTest("partial"):
            response = self.client.get(self.path, {"contacten__naam__contains": "te"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("test", response.data["results"][0]["contacten"][0]["naam"])

        with self.subTest("distinct"):
            producttype.contacten.add(ContactFactory.create(naam="test"))

            response = self.client.get(self.path, {"contacten__naam__contains": "test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("test", response.data["results"][0]["contacten"][0]["naam"])

    def test_locatie_uuid_filter(self):
        uuid = uuid4()

        producttype = ProductTypeFactory.create()
        producttype.locaties.add(LocatieFactory.create(uuid=uuid))

        uuid_2 = uuid4()
        producttype_2 = ProductTypeFactory.create()
        producttype_2.locaties.add(LocatieFactory.create(uuid=uuid_2))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"locaties__uuid": uuid})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(str(uuid), response.data["results"][0]["locaties"][0]["uuid"])

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"locaties__uuid__in": f"{uuid},{uuid_2}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("distinct"):
            uuid_3 = uuid4()
            producttype.locaties.add(LocatieFactory.create(uuid=uuid_3))

            response = self.client.get(
                self.path, {"locaties__uuid__in": f"{uuid},{uuid_3}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_locatie_naam_filter(self):
        producttype = ProductTypeFactory.create()
        producttype.locaties.add(LocatieFactory.create(naam="test"))

        producttype_2 = ProductTypeFactory.create()
        producttype_2.locaties.add(LocatieFactory.create(naam="123"))

        with self.subTest("contains"):
            response = self.client.get(self.path, {"locaties__naam__contains": "test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("test", response.data["results"][0]["locaties"][0]["naam"])

        with self.subTest("partial"):
            response = self.client.get(self.path, {"locaties__naam__contains": "te"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("test", response.data["results"][0]["locaties"][0]["naam"])

        with self.subTest("distinct"):
            producttype.locaties.add(LocatieFactory.create(naam="test"))

            response = self.client.get(self.path, {"locaties__naam__contains": "test"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("test", response.data["results"][0]["locaties"][0]["naam"])

    def test_organisatie_uuid_filter(self):
        uuid = uuid4()

        producttype = ProductTypeFactory.create()
        producttype.organisaties.add(OrganisatieFactory.create(uuid=uuid))

        uuid_2 = uuid4()
        producttype_2 = ProductTypeFactory.create()
        producttype_2.organisaties.add(OrganisatieFactory.create(uuid=uuid_2))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"organisaties__uuid": uuid})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(
                str(uuid), response.data["results"][0]["organisaties"][0]["uuid"]
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"organisaties__uuid__in": f"{uuid},{uuid_2}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("distinct"):
            uuid_3 = uuid4()
            producttype.organisaties.add(OrganisatieFactory.create(uuid=uuid_3))

            response = self.client.get(
                self.path, {"organisaties__uuid__in": f"{uuid},{uuid_3}"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_organisatie_naam_filter(self):
        producttype = ProductTypeFactory.create()
        producttype.organisaties.add(OrganisatieFactory.create(naam="test"))

        producttype_2 = ProductTypeFactory.create()
        producttype_2.organisaties.add(OrganisatieFactory.create(naam="123"))

        with self.subTest("contains"):
            response = self.client.get(
                self.path, {"organisaties__naam__contains": "test"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(
                "test", response.data["results"][0]["organisaties"][0]["naam"]
            )

        with self.subTest("partial"):
            response = self.client.get(
                self.path, {"organisaties__naam__contains": "te"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(
                "test", response.data["results"][0]["organisaties"][0]["naam"]
            )

        with self.subTest("distinct"):
            producttype.organisaties.add(OrganisatieFactory.create(naam="test"))

            response = self.client.get(
                self.path, {"organisaties__naam__contains": "test"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn(
                "test", response.data["results"][0]["organisaties"][0]["naam"]
            )

    def test_organisatie_code_filter(self):
        producttype = ProductTypeFactory.create()
        producttype.organisaties.add(OrganisatieFactory.create(code="ABC"))

        producttype_2 = ProductTypeFactory.create()
        producttype_2.organisaties.add(OrganisatieFactory.create(naam="123"))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"organisaties__code": "ABC"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("ABC", response.data["results"][0]["organisaties"][0]["code"])
