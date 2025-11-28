import datetime
from uuid import uuid4

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from reversion.models import Version

from openproduct.logging.constants import Events
from openproduct.logging.models import TimelineLogProxy
from openproduct.producten.models import Document, Eigenaar, Product, Taak, Zaak
from openproduct.producten.tests.factories import (
    DocumentFactory,
    EigenaarFactory,
    ProductFactory,
    TaakFactory,
    ZaakFactory,
)
from openproduct.producttypen.models.enums import ProductStateChoices
from openproduct.producttypen.tests.factories import (
    JsonSchemaFactory,
    ProductTypeFactory,
    ThemaFactory,
)
from openproduct.urn.models import UrnMappingConfig
from openproduct.utils.tests.cases import BaseApiTestCase


@freeze_time("2024-01-01")
@override_settings(NOTIFICATIONS_DISABLED=True, PRODUCTEN_API_MAJOR_VERSION=0)
class TestProduct(BaseApiTestCase):
    path = reverse_lazy("product-list")

    def setUp(self):
        super().setUp()
        self.thema = ThemaFactory.create()
        self.producttype = ProductTypeFactory.create(
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )

        UrnMappingConfig.objects.create(
            urn="maykin:abc:ztc:zaak",
            url="https://maykin.ztc.com/api/v1/zaken",
        )

        UrnMappingConfig.objects.create(
            urn="maykin:abc:ztc:taak",
            url="https://maykin.ztc.com/api/v1/taken",
        )

        UrnMappingConfig.objects.create(
            urn="maykin:abc:ztc:document",
            url="https://maykin.ztc.com/api/v1/documenten",
        )

        self.producttype.themas.add(self.thema)
        self.data = {
            "producttype_uuid": self.producttype.uuid,
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

    def detail_path(self, product):
        return reverse("product-detail", args=[product.uuid])

    def test_read_product_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "producttype_uuid": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "eigenaren": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
            },
        )

    def test_create_product(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        producttype = product.producttype
        thema = producttype.themas.first()
        expected_data = {
            "url": f"http://testserver{self.detail_path(product)}",
            "uuid": str(product.uuid),
            "status": product.status,
            "verbruiksobject": None,
            "dataobject": None,
            "gepubliceerd": False,
            "naam": "",
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "uuid": str(product.eigenaren.get().uuid),
                }
            ],
            "documenten": [],
            "zaken": [],
            "taken": [],
            "producttype": {
                "uuid": str(producttype.uuid),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
                "publicatie_start_datum": "2024-01-01",
                "publicatie_eind_datum": None,
                "keywords": [],
                "themas": [
                    {
                        "uuid": str(thema.uuid),
                        "hoofd_thema": None,
                        "gepubliceerd": True,
                        "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": thema.update_datum.astimezone().isoformat(),
                        "naam": thema.naam,
                        "beschrijving": thema.beschrijving,
                    }
                ],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_verbruiksobject(self):
        json_schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )

        self.producttype.verbruiksobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"verbruiksobject": {"naam": "Test"}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        producttype = product.producttype
        thema = producttype.themas.first()
        expected_data = {
            "uuid": str(product.uuid),
            "url": f"http://testserver{self.detail_path(product)}",
            "status": product.status,
            "verbruiksobject": {"naam": "Test"},
            "dataobject": None,
            "gepubliceerd": False,
            "naam": "",
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "uuid": str(product.eigenaren.get().uuid),
                }
            ],
            "documenten": [],
            "zaken": [],
            "taken": [],
            "producttype": {
                "uuid": str(producttype.uuid),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "publicatie_start_datum": "2024-01-01",
                "publicatie_eind_datum": None,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "uuid": str(thema.uuid),
                        "hoofd_thema": None,
                        "gepubliceerd": True,
                        "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": thema.update_datum.astimezone().isoformat(),
                        "naam": thema.naam,
                        "beschrijving": thema.beschrijving,
                    }
                ],
            },
        }
        self.assertEqual(response.data, expected_data)

    @freeze_time("2024-1-1")
    def test_create_product_with_start_datum_set_to_today_changes_state_to_active(self):
        producttype = ProductTypeFactory(
            toegestane_statussen=[ProductStateChoices.ACTIEF]
        )

        data = self.data | {
            "producttype_uuid": producttype.uuid,
            "start_datum": datetime.date(2024, 1, 1),
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], ProductStateChoices.ACTIEF)

    @freeze_time("2024-1-1")
    def test_create_product_with_eind_datum_set_to_today_changes_state_to_verlopen(
        self,
    ):
        producttype = ProductTypeFactory(
            toegestane_statussen=[ProductStateChoices.VERLOPEN]
        )

        data = self.data | {
            "producttype_uuid": producttype.uuid,
            "eind_datum": datetime.date(2024, 1, 1),
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], ProductStateChoices.VERLOPEN)

    def test_create_product_with_invalid_verbruiksobject(self):
        json_schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )

        self.producttype.verbruiksobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"verbruiksobject": {"naam": 123}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "verbruiksobject": [
                    ErrorDetail(
                        string=_(
                            "Het verbruiksobject komt niet overeen met het schema gedefinieerd op het producttype."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_dataobject(self):
        json_schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )

        self.producttype.dataobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"dataobject": {"naam": "Test"}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        producttype = product.producttype
        thema = producttype.themas.first()
        expected_data = {
            "uuid": str(product.uuid),
            "url": f"http://testserver{self.detail_path(product)}",
            "naam": "",
            "status": product.status,
            "verbruiksobject": None,
            "dataobject": {"naam": "Test"},
            "gepubliceerd": False,
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": product.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product.update_datum.astimezone().isoformat(),
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "aanvraag_zaak_url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "uuid": str(product.eigenaren.get().uuid),
                }
            ],
            "documenten": [],
            "zaken": [],
            "taken": [],
            "producttype": {
                "uuid": str(producttype.uuid),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "gepubliceerd": True,
                "publicatie_start_datum": "2024-01-01",
                "publicatie_eind_datum": None,
                "toegestane_statussen": ["gereed"],
                "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "uuid": str(thema.uuid),
                        "hoofd_thema": None,
                        "gepubliceerd": True,
                        "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": thema.update_datum.astimezone().isoformat(),
                        "naam": thema.naam,
                        "beschrijving": thema.beschrijving,
                    }
                ],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_create_product_with_invalid_dataobject(self):
        json_schema = JsonSchemaFactory.create(
            schema={
                "type": "object",
                "properties": {"naam": {"type": "string"}},
                "required": ["naam"],
            },
        )

        self.producttype.dataobject_schema = json_schema
        self.producttype.save()

        data = self.data | {"dataobject": {"naam": 123}}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "dataobject": [
                    ErrorDetail(
                        string="Het dataobject komt niet overeen met het schema gedefinieerd op het producttype.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_not_allowed_state(self):
        data = self.data | {"status": "actief"}
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    ErrorDetail(
                        string=_(
                            "Status 'Actief' is niet toegestaan voor het producttype {}."
                        ).format(self.producttype.naam),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_allowed_state(self):
        data = self.data | {"status": "gereed"}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_with_eigenaren(self):
        data = self.data | {
            "eigenaren": [
                {"bsn": "111222333"},
                {"kvk_nummer": "11122233"},
                {"klantnummer": "123"},
            ]
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 3)

    def test_create_product_with_eigenaar_with_uuid(self):
        uuid = uuid4()
        data = self.data | {
            "eigenaren": [
                {"uuid": uuid, "kvk_nummer": "11122233"},
            ]
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 1)
        self.assertNotEqual(Eigenaar.objects.get().uuid, uuid)

    def test_create_product_with_empty_eigenaar(self):
        data = self.data | {"eigenaren": [{}]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenaren": [
                    {
                        "model_errors": [
                            ErrorDetail(
                                string=_(
                                    "Een eigenaar moet een bsn (en/of klantnummer) of een kvk nummer (met of zonder vestigingsnummer) hebben."
                                ),
                                code="invalid",
                            )
                        ]
                    }
                ]
            },
        )

    def test_create_product_with_vestigingsnummer_only(self):
        data = self.data | {"eigenaren": [{"vestigingsnummer": "123"}]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenaren": [
                    {
                        "vestigingsnummer": [
                            ErrorDetail(
                                string="Een vestigingsnummer kan alleen in combinatie met een kvk nummer worden ingevuld.",
                                code="invalid",
                            )
                        ]
                    }
                ]
            },
        )

    def test_create_product_without_eigenaren(self):
        response = self.client.post(self.path, self.data | {"eigenaren": []})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "eigenaren": [
                    ErrorDetail(
                        string=_("Er is minimaal één eigenaar vereist."),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_product_with_vestigingsnummer_and_kvk(self):
        data = self.data | {
            "eigenaren": [{"vestingsnummer": "123", "kvk_nummer": "12345678"}]
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 1)

    def test_create_product_creates_log_and_history(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.get()

        log = TimelineLogProxy.objects.filter(
            content_type__exact=ContentType.objects.get_for_model(product).pk,
            object_id=product.pk,
        ).get()

        self.assertEqual(log.event, Events.create)
        self.assertEqual(Version.objects.get_for_object(product).count(), 1)

    def test_create_product_with_external_objects(self):
        data = self.data | {
            "zaken": [
                {"urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"}
            ],
            "taken": [
                {"urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1"}
            ],
            "documenten": [
                {"urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1"}
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Zaak.objects.count(), 1)
        self.assertEqual(
            Zaak.objects.first().url,
            "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        self.assertEqual(Taak.objects.count(), 1)
        self.assertEqual(
            Taak.objects.first().url,
            "https://maykin.ztc.com/api/v1/taken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            Document.objects.first().url,
            "https://maykin.ztc.com/api/v1/documenten/d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

    def test_create_product_with_duplicate_zaken(self):
        with self.subTest("duplicate urns"):
            zaken = [
                {"urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"},
                {"urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"},
            ]
            data = self.data | {"zaken": zaken}
            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest("duplicate urls"):
            zaken = [
                {
                    "url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1"
                },
                {
                    "url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1"
                },
            ]
            data = self.data | {"zaken": zaken}
            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_duplicate_taken(self):
        with self.subTest("duplicate urns"):
            taken = [
                {"urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1"},
                {"urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1"},
            ]
            data = self.data | {"taken": taken}
            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest("duplicate urls"):
            taken = [
                {
                    "url": "https://maykin.ztc.com/api/v1/taken/d42613cd-ee22-4455-808c-c19c7b8442a1"
                },
                {
                    "url": "https://maykin.ztc.com/api/v1/taken/d42613cd-ee22-4455-808c-c19c7b8442a1"
                },
            ]
            data = self.data | {"taken": taken}
            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_duplicate_documenten(self):
        with self.subTest("duplicate urns"):
            documenten = [
                {"urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1"},
                {"urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1"},
            ]
            data = self.data | {"documenten": documenten}
            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest("duplicate urls"):
            documenten = [
                {
                    "url": "https://maykin.ztc.com/api/v1/documenten/d42613cd-ee22-4455-808c-c19c7b8442a1"
                },
                {
                    "url": "https://maykin.ztc.com/api/v1/documenten/d42613cd-ee22-4455-808c-c19c7b8442a1"
                },
            ]
            data = self.data | {"documenten": documenten}
            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_free_product(self):
        data = self.data | {"prijs": 0}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eigenaar.objects.count(), 1)
        self.assertEqual(response.data["prijs"], "0.00")

    def test_update_product(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=["verlopen"])
        product = ProductFactory.create(producttype=producttype)

        data = self.data | {
            "eind_datum": datetime.date(2025, 12, 31),
            "producttype_uuid": producttype.uuid,
            "eigenaren": [{"kvk_nummer": "12345678"}],
        }
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().eind_datum, data["eind_datum"])

    @freeze_time("2024-1-1")
    def test_update_product_with_start_datum_set_to_today_changes_state_to_active(self):
        producttype = ProductTypeFactory(
            toegestane_statussen=[ProductStateChoices.ACTIEF]
        )
        product = ProductFactory.create(producttype=producttype)

        data = self.data | {
            "producttype_uuid": producttype.uuid,
            "start_datum": datetime.date(2024, 1, 1),
        }

        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ProductStateChoices.ACTIEF)

    @freeze_time("2024-1-1")
    def test_update_product_with_eind_datum_set_to_today_changes_state_to_verlopen(
        self,
    ):
        producttype = ProductTypeFactory(
            toegestane_statussen=[ProductStateChoices.VERLOPEN]
        )
        product = ProductFactory.create(producttype=producttype)

        data = self.data | {
            "producttype_uuid": producttype.uuid,
            "eind_datum": datetime.date(2024, 1, 1),
        }

        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ProductStateChoices.VERLOPEN)

    def test_update_product_with_not_allowed_state(self):
        product = ProductFactory.create()
        data = self.data.copy() | {"status": "actief"}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    ErrorDetail(
                        string=_(
                            "Status 'Actief' is niet toegestaan voor het producttype {}."
                        ).format(self.producttype.naam),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_product_removing_eigenaren(self):
        product = ProductFactory.create()
        EigenaarFactory.create(product=product, bsn="111222333")
        EigenaarFactory.create(product=product, kvk_nummer="12345678")

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_("Er is minimaal één eigenaar vereist."),
                    code="invalid",
                )
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(
                self.detail_path(product), self.data | {"eigenaren": []}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Eigenaar.objects.count(), 2)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), {"eigenaren": []})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Eigenaar.objects.count(), 2)
            self.assertEqual(response.data, expected_error)

    def test_update_updating_and_removing_eigenaren(self):
        product = ProductFactory.create()
        eigenaar_to_be_updated = EigenaarFactory.create(
            product=product, bsn="111222333"
        )
        EigenaarFactory.create(product=product, kvk_nummer="12345678")

        self.maxDiff = None

        data = {
            "eigenaren": [
                {
                    "uuid": eigenaar_to_be_updated.uuid,
                    "klantnummer": "1234",
                    "bsn": "",
                }
            ]
        }

        expected_data = [
            {
                "uuid": str(eigenaar_to_be_updated.uuid),
                "klantnummer": "1234",
                "bsn": "",
                "kvk_nummer": "",
                "vestigingsnummer": "",
            }
        ]

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(response.data["eigenaren"], expected_data)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(response.data["eigenaren"], expected_data)

    def test_update_creating_and_removing_eigenaren(self):
        product = ProductFactory.create()
        EigenaarFactory.create(product=product, kvk_nummer="12345678")

        data = {"eigenaren": [{"klantnummer": "1234"}]}

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(Eigenaar.objects.get().klantnummer, "1234")

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Eigenaar.objects.count(), 1)
            self.assertEqual(Eigenaar.objects.get().klantnummer, "1234")

    def test_update_product_with_eigenaar_not_part_of_product(self):
        product = ProductFactory.create()
        eigenaar_of_other_product = EigenaarFactory.create(kvk_nummer="12345678")

        data = {
            "eigenaren": [
                {"uuid": eigenaar_of_other_product.uuid, "klantnummer": "1234"}
            ]
        }

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_(
                        "Eigenaar uuid {} op index 0 is niet onderdeel van het Product object."
                    ).format(eigenaar_of_other_product.uuid),
                    code="invalid",
                )
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

    def test_update_product_with_eigenaar_uuid_not_existing(self):
        product = ProductFactory.create()

        eigenaar_uuid = uuid4()

        data = {"eigenaren": [{"uuid": eigenaar_uuid, "klantnummer": "1234"}]}

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_("Eigenaar uuid {} op index 0 bestaat niet.").format(
                        eigenaar_uuid
                    ),
                    code="invalid",
                )
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

    def test_update_product_with_duplicate_eigenaren_uuids(self):
        product = ProductFactory.create()
        eigenaar_to_be_updated = EigenaarFactory.create(
            product=product, bsn="111222333"
        )

        expected_error = {
            "eigenaren": [
                ErrorDetail(
                    string=_("Dubbel uuid: {} op index 1.").format(
                        eigenaar_to_be_updated.uuid
                    ),
                    code="invalid",
                )
            ]
        }

        data = {
            "eigenaren": [
                {"uuid": eigenaar_to_be_updated.uuid, "klantnummer": "1234"},
                {"uuid": eigenaar_to_be_updated.uuid, "klantnummer": "5678"},
            ]
        }

        with self.subTest("PUT"):
            response = self.client.put(self.detail_path(product), self.data | data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

        with self.subTest("PATCH"):
            response = self.client.patch(self.detail_path(product), data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, expected_error)

    def test_update_product_creates_log_and_history(self):
        product = ProductFactory.create()

        response = self.client.put(self.detail_path(product), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)

        log = TimelineLogProxy.objects.filter(
            content_type__exact=ContentType.objects.get_for_model(product).pk,
            object_id=product.pk,
        ).get()

        self.assertEqual(log.event, Events.update)
        # version is not created with factoryboy
        self.assertEqual(Version.objects.get_for_object(product).count(), 1)

    def test_update_product_with_document(self):
        product = ProductFactory.create()

        documenten = [
            {"urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1"}
        ]
        data = self.data | {"documenten": documenten}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            response.data["documenten"],
            [
                {
                    "urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "url": "https://maykin.ztc.com/api/v1/documenten/d42613cd-ee22-4455-808c-c19c7b8442a1",
                }
            ],
        )

    def test_update_product_with_document_replacing_existing(self):
        product = ProductFactory.create()

        DocumentFactory.create(product=product)

        documenten = [
            {"urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1"}
        ]
        data = self.data | {"documenten": documenten}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            response.data["documenten"],
            [
                {
                    "urn": "maykin:abc:ztc:document:d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "url": "https://maykin.ztc.com/api/v1/documenten/d42613cd-ee22-4455-808c-c19c7b8442a1",
                }
            ],
        )

    def test_update_product_removing_documenten(self):
        product = ProductFactory.create()
        DocumentFactory.create(product=product)
        DocumentFactory.create(product=product)

        documenten = []
        data = self.data | {"documenten": documenten}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(response.data["documenten"], documenten)

    def test_update_product_existing_documenten_are_kept(self):
        product = ProductFactory.create()
        DocumentFactory.create(product=product)

        response = self.client.put(self.detail_path(product), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 1)

    def test_update_product_with_zaak(self):
        product = ProductFactory.create()

        zaken = [{"urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"}]
        data = self.data | {"zaken": zaken}
        response = self.client.put(self.detail_path(product), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 1)
        self.assertEqual(
            response.data["zaken"],
            [
                {
                    "urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                }
            ],
        )

    def test_update_product_with_zaak_replacing_existing(self):
        product = ProductFactory.create()

        ZaakFactory.create(product=product)

        zaken = [
            {
                "urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            }
        ]
        data = self.data | {"zaken": zaken}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 1)
        self.assertEqual(
            response.data["zaken"],
            [
                {
                    "urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "url": "https://maykin.ztc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                }
            ],
        )

    def test_update_product_removing_zaken(self):
        product = ProductFactory.create()
        ZaakFactory.create(product=product)
        ZaakFactory.create(product=product)

        zaken = []
        data = self.data | {"zaken": zaken}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 0)
        self.assertEqual(response.data["zaken"], zaken)

    def test_update_product_existing_zaken_are_kept(self):
        product = ProductFactory.create()
        ZaakFactory.create(product=product)

        response = self.client.put(self.detail_path(product), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 1)

    def test_update_product_with_taak(self):
        product = ProductFactory.create()

        taken = [{"urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1"}]
        data = self.data | {"taken": taken}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 1)
        self.assertEqual(
            response.data["taken"],
            [
                {
                    "urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "url": "https://maykin.ztc.com/api/v1/taken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                }
            ],
        )

    def test_update_product_with_taak_replacing_existing(self):
        product = ProductFactory.create()

        TaakFactory.create(product=product)

        taken = [
            {
                "urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            }
        ]
        data = self.data | {"taken": taken}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 1)
        self.assertEqual(
            response.data["taken"],
            [
                {
                    "urn": "maykin:abc:ztc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1",
                    "url": "https://maykin.ztc.com/api/v1/taken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                }
            ],
        )

    def test_update_product_removing_taken(self):
        product = ProductFactory.create()
        TaakFactory.create(product=product)
        TaakFactory.create(product=product)

        taken = []
        data = self.data | {"taken": taken}
        response = self.client.put(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 0)
        self.assertEqual(response.data["taken"], taken)

    def test_update_product_existing_taken_are_kept(self):
        product = ProductFactory.create()
        TaakFactory.create(product=product)

        response = self.client.put(self.detail_path(product), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 1)

    def test_partial_update_product(self):
        product = ProductFactory.create(
            producttype=ProductTypeFactory.create(toegestane_statussen=["verlopen"]),
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

        data = {"eind_datum": datetime.date(2025, 12, 31)}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().eind_datum, data["eind_datum"])

    def test_partial_update_product_with_document(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        documenten = [
            {"urn": "maykin:abc:ztc:document:99a8bd4f-4144-4105-9850-e477628852fc"}
        ]
        data = {"documenten": documenten}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            response.data["documenten"],
            [
                {
                    "urn": "maykin:abc:ztc:document:99a8bd4f-4144-4105-9850-e477628852fc",
                    "url": "https://maykin.ztc.com/api/v1/documenten/99a8bd4f-4144-4105-9850-e477628852fc",
                }
            ],
        )

    def test_partial_update_product_with_document_replacing_existing(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        DocumentFactory.create(product=product)

        documenten = [
            {"urn": "maykin:abc:ztc:document:99a8bd4f-4144-4105-9850-e477628852fc"}
        ]
        data = {"documenten": documenten}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            response.data["documenten"],
            [
                {
                    "urn": "maykin:abc:ztc:document:99a8bd4f-4144-4105-9850-e477628852fc",
                    "url": "https://maykin.ztc.com/api/v1/documenten/99a8bd4f-4144-4105-9850-e477628852fc",
                }
            ],
        )

    def test_partial_update_product_removing_documenten(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )
        DocumentFactory.create(product=product)
        DocumentFactory.create(product=product)

        documenten = []
        data = {"documenten": documenten}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(response.data["documenten"], documenten)

    def test_partial_update_product_existing_documenten_are_kept(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )
        DocumentFactory.create(product=product)

        response = self.client.patch(self.detail_path(product), {"prijs": "10"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.count(), 1)

    def test_partial_update_product_with_zaak(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        zaken = [{"urn": "maykin:abc:ztc:zaak:99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"zaken": zaken}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 1)
        self.assertEqual(
            response.data["zaken"],
            [
                {
                    "urn": "maykin:abc:ztc:zaak:99a8bd4f-4144-4105-9850-e477628852fc",
                    "url": "https://maykin.ztc.com/api/v1/zaken/99a8bd4f-4144-4105-9850-e477628852fc",
                }
            ],
        )

    def test_partial_update_product_with_zaak_replacing_existing(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        ZaakFactory.create(product=product)

        zaken = [{"urn": "maykin:abc:ztc:zaak:99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"zaken": zaken}
        response = self.client.patch(self.detail_path(product), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 1)
        self.assertEqual(
            response.data["zaken"],
            [
                {
                    "urn": "maykin:abc:ztc:zaak:99a8bd4f-4144-4105-9850-e477628852fc",
                    "url": "https://maykin.ztc.com/api/v1/zaken/99a8bd4f-4144-4105-9850-e477628852fc",
                }
            ],
        )

    def test_partial_update_product_removing_zaken(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )
        ZaakFactory.create(product=product)
        ZaakFactory.create(product=product)

        zaken = []
        data = {"zaken": zaken}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 0)
        self.assertEqual(response.data["zaken"], zaken)

    def test_partial_update_product_existing_zaken_are_kept(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )
        ZaakFactory.create(product=product)

        response = self.client.patch(self.detail_path(product), {"prijs": "10"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Zaak.objects.count(), 1)

    def test_partial_update_product_with_taak(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        taken = [{"urn": "maykin:abc:ztc:taak:99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"taken": taken}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 1)
        self.assertEqual(
            response.data["taken"],
            [
                {
                    "urn": "maykin:abc:ztc:taak:99a8bd4f-4144-4105-9850-e477628852fc",
                    "url": "https://maykin.ztc.com/api/v1/taken/99a8bd4f-4144-4105-9850-e477628852fc",
                }
            ],
        )

    def test_partial_update_product_with_taak_replacing_existing(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )

        TaakFactory.create(product=product)

        taken = [{"urn": "maykin:abc:ztc:taak:99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"taken": taken}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 1)
        self.assertEqual(
            response.data["taken"],
            [
                {
                    "urn": "maykin:abc:ztc:taak:99a8bd4f-4144-4105-9850-e477628852fc",
                    "url": "https://maykin.ztc.com/api/v1/taken/99a8bd4f-4144-4105-9850-e477628852fc",
                }
            ],
        )

    def test_partial_update_product_removing_taken(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )
        TaakFactory.create(product=product)
        TaakFactory.create(product=product)

        taken = []
        data = {"taken": taken}
        response = self.client.patch(self.detail_path(product), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 0)
        self.assertEqual(response.data["taken"], taken)

    def test_partial_update_product_existing_taken_are_kept(self):
        product = ProductFactory.create(
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        )
        TaakFactory.create(product=product)

        response = self.client.patch(self.detail_path(product), {"prijs": "10"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Taak.objects.count(), 1)

    def test_read_producten(self):
        product1 = ProductFactory.create(
            producttype=self.producttype,
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        EigenaarFactory(kvk_nummer="12345678", product=product1)
        product2 = ProductFactory.create(
            producttype=self.producttype,
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        EigenaarFactory(kvk_nummer="12345678", product=product2)

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "url": f"http://testserver{self.detail_path(product1)}",
                "uuid": str(product1.uuid),
                "status": product1.status,
                "verbruiksobject": None,
                "dataobject": None,
                "gepubliceerd": False,
                "naam": "",
                "start_datum": None,
                "eind_datum": None,
                "prijs": str(product1.prijs),
                "frequentie": product1.frequentie,
                "aanmaak_datum": product1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product1.update_datum.astimezone().isoformat(),
                "aanvraag_zaak_urn": product1.aanvraag_zaak_urn,
                "aanvraag_zaak_url": product1.aanvraag_zaak_url,
                "eigenaren": [
                    {
                        "bsn": "",
                        "kvk_nummer": "12345678",
                        "vestigingsnummer": "",
                        "klantnummer": "",
                        "uuid": str(product1.eigenaren.get().uuid),
                    }
                ],
                "documenten": [],
                "zaken": [],
                "taken": [],
                "producttype": {
                    "uuid": str(self.producttype.uuid),
                    "code": self.producttype.code,
                    "uniforme_product_naam": self.producttype.uniforme_product_naam.naam,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "publicatie_start_datum": "2024-01-01",
                    "publicatie_eind_datum": None,
                    "aanmaak_datum": self.producttype.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.producttype.update_datum.astimezone().isoformat(),
                    "keywords": [],
                    "themas": [
                        {
                            "uuid": str(self.thema.uuid),
                            "hoofd_thema": None,
                            "gepubliceerd": True,
                            "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                            "update_datum": self.thema.update_datum.astimezone().isoformat(),
                            "naam": self.thema.naam,
                            "beschrijving": self.thema.beschrijving,
                        }
                    ],
                },
            },
            {
                "url": f"http://testserver{self.detail_path(product2)}",
                "uuid": str(product2.uuid),
                "status": product2.status,
                "verbruiksobject": None,
                "dataobject": None,
                "gepubliceerd": False,
                "naam": "",
                "start_datum": None,
                "eind_datum": None,
                "prijs": str(product2.prijs),
                "frequentie": product2.frequentie,
                "aanmaak_datum": product2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product2.update_datum.astimezone().isoformat(),
                "aanvraag_zaak_urn": product2.aanvraag_zaak_urn,
                "aanvraag_zaak_url": product2.aanvraag_zaak_url,
                "eigenaren": [
                    {
                        "bsn": "",
                        "kvk_nummer": "12345678",
                        "vestigingsnummer": "",
                        "klantnummer": "",
                        "uuid": str(product2.eigenaren.get().uuid),
                    }
                ],
                "documenten": [],
                "zaken": [],
                "taken": [],
                "producttype": {
                    "uuid": str(self.producttype.uuid),
                    "code": self.producttype.code,
                    "uniforme_product_naam": self.producttype.uniforme_product_naam.naam,
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "publicatie_start_datum": "2024-01-01",
                    "publicatie_eind_datum": None,
                    "aanmaak_datum": self.producttype.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.producttype.update_datum.astimezone().isoformat(),
                    "keywords": [],
                    "themas": [
                        {
                            "uuid": str(self.thema.uuid),
                            "hoofd_thema": None,
                            "gepubliceerd": True,
                            "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                            "update_datum": self.thema.update_datum.astimezone().isoformat(),
                            "naam": self.thema.naam,
                            "beschrijving": self.thema.beschrijving,
                        }
                    ],
                },
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    @freeze_time("2025-12-31")
    def test_read_product(self):
        thema = ThemaFactory.create()
        producttype = ProductTypeFactory.create(
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )
        producttype.themas.add(thema)
        product = ProductFactory.create(
            producttype=producttype,
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        EigenaarFactory(kvk_nummer="12345678", product=product)

        response = self.client.get(self.detail_path(product))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "url": f"http://testserver{self.detail_path(product)}",
            "uuid": str(product.uuid),
            "status": product.status,
            "verbruiksobject": None,
            "dataobject": None,
            "gepubliceerd": False,
            "naam": "",
            "start_datum": None,
            "eind_datum": None,
            "prijs": str(product.prijs),
            "frequentie": product.frequentie,
            "aanmaak_datum": "2025-12-31T01:00:00+01:00",
            "update_datum": "2025-12-31T01:00:00+01:00",
            "aanvraag_zaak_urn": product.aanvraag_zaak_urn,
            "aanvraag_zaak_url": product.aanvraag_zaak_url,
            "eigenaren": [
                {
                    "bsn": "",
                    "kvk_nummer": "12345678",
                    "vestigingsnummer": "",
                    "klantnummer": "",
                    "uuid": str(product.eigenaren.get().uuid),
                }
            ],
            "documenten": [],
            "zaken": [],
            "taken": [],
            "producttype": {
                "uuid": str(producttype.uuid),
                "code": producttype.code,
                "uniforme_product_naam": producttype.uniforme_product_naam.naam,
                "toegestane_statussen": ["gereed"],
                "gepubliceerd": True,
                "publicatie_start_datum": "2024-01-01",
                "publicatie_eind_datum": None,
                "aanmaak_datum": "2025-12-31T01:00:00+01:00",
                "update_datum": "2025-12-31T01:00:00+01:00",
                "keywords": [],
                "themas": [
                    {
                        "uuid": str(thema.uuid),
                        "hoofd_thema": None,
                        "gepubliceerd": True,
                        "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": thema.update_datum.astimezone().isoformat(),
                        "naam": thema.naam,
                        "beschrijving": thema.beschrijving,
                    }
                ],
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_product(self):
        product = ProductFactory.create()
        response = self.client.delete(self.detail_path(product))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_creates_log(self):
        product = ProductFactory.create()
        response = self.client.delete(self.detail_path(product))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

        log = TimelineLogProxy.objects.filter(
            content_type__exact=ContentType.objects.get_for_model(product).pk,
            object_id=product.pk,
        ).get()

        self.assertEqual(log.event, Events.delete)

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_not_checked_when_not_changed(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])

        data = {
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "frequentie": "eenmalig",
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        product = ProductFactory.create(producttype=producttype, **data)

        response = self.client.put(
            self.detail_path(product),
            data
            | {
                "eigenaren": [{"kvk_nummer": "12345678"}],
                "producttype_uuid": producttype.uuid,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @freeze_time("2025-11-30")
    def test_partial_update_state_and_dates_are_not_checked_when_not_changed(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])

        data = {
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        product = ProductFactory.create(producttype=producttype, **data)

        response = self.client.patch(self.detail_path(product), {"prijs": "50"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_checked_when_producttype_is_changed(self):
        new_producttype = ProductTypeFactory.create(toegestane_statussen=[])

        tests = [
            {
                "field": {"status": "gereed"},
                "error": {
                    "status": [
                        ErrorDetail(
                            string=_(
                                "Status 'Gereed' is niet toegestaan voor het producttype {}."
                            ).format(new_producttype.naam),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"start_datum": datetime.date(2025, 12, 31)},
                "error": {
                    "start_datum": [
                        ErrorDetail(
                            string=_(
                                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het producttype."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"eind_datum": datetime.date(2026, 12, 31)},
                "error": {
                    "eind_datum": [
                        ErrorDetail(
                            string=_(
                                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het producttype."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
        ]

        for test in tests:
            with self.subTest(
                f"Test {test['field']} is checked when producttype is changed."
            ):
                data = {
                    "prijs": "10",
                    "frequentie": "eenmalig",
                } | test["field"]

                product = ProductFactory.create(
                    producttype=ProductTypeFactory.create(), **data
                )
                EigenaarFactory(product=product)

                response = self.client.put(
                    self.detail_path(product),
                    data
                    | {
                        "producttype_uuid": new_producttype.uuid,
                        "eigenaren": [{"kvk_nummer": "12345678"}],
                    },
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(response.data, test["error"])

    @freeze_time("2025-11-30")
    def test_update_state_and_dates_are_checked_when_changed(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=[])
        tests = [
            {
                "field": {"status": "gereed"},
                "error": {
                    "status": [
                        ErrorDetail(
                            string=_(
                                "Status 'Gereed' is niet toegestaan voor het producttype {}."
                            ).format(producttype.naam),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"start_datum": datetime.date(2025, 12, 31)},
                "error": {
                    "start_datum": [
                        ErrorDetail(
                            string=_(
                                "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het producttype."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
            {
                "field": {"eind_datum": datetime.date(2026, 12, 31)},
                "error": {
                    "eind_datum": [
                        ErrorDetail(
                            string=_(
                                "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het producttype."
                            ),
                            code="invalid",
                        )
                    ]
                },
            },
        ]

        for test in tests:
            with self.subTest(
                f"Test {test['field']} is checked when producttype is changed."
            ):
                data = {
                    "status": "initieel",
                    "prijs": "10",
                    "frequentie": "eenmalig",
                }

                product = ProductFactory.create(producttype=producttype, **data)

                response = self.client.put(
                    self.detail_path(product),
                    data
                    | test["field"]
                    | {
                        "eigenaren": [{"kvk_nummer": "12345678"}],
                        "producttype_uuid": producttype.uuid,
                    },
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(response.data, test["error"])


@override_settings(NOTIFICATIONS_DISABLED=True)
class TestProductUrns(BaseApiTestCase):
    path = reverse_lazy("product-list")

    def setUp(self):
        super().setUp()
        self.thema = ThemaFactory.create()
        self.producttype = ProductTypeFactory.create(
            toegestane_statussen=["gereed"],
            publicatie_start_datum=datetime.date(2024, 1, 1),
        )
        self.producttype.themas.add(self.thema)
        self.data = {
            "producttype_uuid": self.producttype.uuid,
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "eigenaren": [{"kvk_nummer": "12345678"}],
        }

    def detail_path(self, product):
        return reverse("product-detail", args=[product.uuid])

    def test_invalid_urns(self):
        with self.subTest("None"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_urn": None}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["een url of urn is verplicht"]},
            )

        with self.subTest("empty"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_urn": ""}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["een url of urn is verplicht"]},
            )

        with self.subTest("string"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_urn": "a"}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak_urn": ["Voer een geldige waarde in."]},
            )

        with self.subTest("::::"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_urn": "::::::"}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak_urn": ["Voer een geldige waarde in."]},
            )

        with self.subTest("::::"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_urn": ":a:b:c:d:e"}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak_urn": ["Voer een geldige waarde in."]},
            )

    def test_invalid_urls(self):
        with self.subTest("None"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_url": None}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["een url of urn is verplicht"]},
            )

        with self.subTest("empty"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_url": ""}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["een url of urn is verplicht"]},
            )

        with self.subTest("string"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_url": "a"}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak_url": ["Voer een geldige URL in."]},
            )

        with self.subTest("slash"):
            response = self.client.post(
                self.path, self.data | {"aanvraag_zaak_url": "/awdaw"}
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak_url": ["Voer een geldige URL in."]},
            )

        with self.subTest("url"):
            response = self.client.post(
                self.path,
                self.data | {"aanvraag_zaak_url": "https://google/128937-012837-adawd"},
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak_url": ["Voer een geldige URL in."]},
            )

    def test_create_product_without_aanvraag_zaak(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"aanvraag_zaak": ["een url of urn is verplicht"]},
        )

    def test_create_product_with_different_urn_urls(self):
        data = self.data | {
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "aanvraag_zaak_url": "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a2",
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"aanvraag_zaak": ["de uuid van de url en urn komen niet overeen"]},
        )

    def test_create_product_with_urn_only(self):
        data = self.data | {
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1"
        }

        with self.subTest("mapping required"):
            with override_settings(REQUIRE_URN_URL_MAPPING=True):
                response = self.client.post(self.path, data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(
                    response.json(),
                    {"aanvraag_zaak": ["de urn heeft geen mapping"]},
                )

        with self.subTest("allowed"):
            with override_settings(REQUIRE_URN_URL_MAPPING=False):
                response = self.client.post(self.path, data)

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

                self.assertEqual(
                    response.data["aanvraag_zaak_urn"],
                    "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
                )
                self.assertEqual(response.data["aanvraag_zaak_url"], None)

                product = Product.objects.get(uuid=response.data["uuid"])
                self.assertEqual(
                    product.aanvraag_zaak_urn,
                    "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
                )
                self.assertEqual(product.aanvraag_zaak_url, None)

        with self.subTest("in mapping"):
            UrnMappingConfig.objects.create(
                urn="maykin:abc:ztc:zaak", url="https://maykin.ztc.com/zaken"
            )

            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertEqual(
                response.data["aanvraag_zaak_urn"],
                "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            )
            self.assertEqual(
                response.data["aanvraag_zaak_url"],
                "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            )

            product = Product.objects.get(uuid=response.data["uuid"])
            self.assertEqual(
                product.aanvraag_zaak_urn,
                "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            )
            self.assertEqual(
                product.aanvraag_zaak_url,
                "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            )

    def test_create_product_with_url_only(self):
        data = self.data | {
            "aanvraag_zaak_url": "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1"
        }

        with self.subTest("mapping required"):
            with override_settings(REQUIRE_URL_URN_MAPPING=True):
                response = self.client.post(self.path, data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(
                    response.json(),
                    {"aanvraag_zaak": ["de url heeft geen mapping"]},
                )

        with self.subTest("allowed"):
            with override_settings(REQUIRE_URL_URN_MAPPING=False):
                response = self.client.post(self.path, data)

                self.assertEqual(
                    response.status_code, status.HTTP_201_CREATED, response.data
                )

                self.assertEqual(
                    response.data["aanvraag_zaak_url"],
                    "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                )
                self.assertEqual(response.data["aanvraag_zaak_urn"], None)

                product = Product.objects.get(uuid=response.data["uuid"])
                self.assertEqual(
                    product.aanvraag_zaak_url,
                    "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
                )
                self.assertEqual(product.aanvraag_zaak_urn, None)

        with self.subTest("in mapping"):
            UrnMappingConfig.objects.create(
                urn="maykin:abc:ztc:zaak", url="https://maykin.ztc.com/zaken"
            )

            response = self.client.post(self.path, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertEqual(
                response.data["aanvraag_zaak_urn"],
                "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            )
            self.assertEqual(
                response.data["aanvraag_zaak_url"],
                "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            )

            product = Product.objects.get(uuid=response.data["uuid"])
            self.assertEqual(
                product.aanvraag_zaak_urn,
                "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            )
            self.assertEqual(
                product.aanvraag_zaak_url,
                "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            )

    def test_create_product_with_urn_and_url(self):
        data = self.data | {
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "aanvraag_zaak_url": "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        with self.subTest("different mappings"):
            UrnMappingConfig.objects.create(
                urn="maykin:abc:ztc:zaak", url="https://maykin.ztc.com/zaken"
            )
            UrnMappingConfig.objects.create(
                urn="maykin:abc:ztc:zaakabc", url="https://maykin.ztc.com/zaken2"
            )

            response = self.client.post(
                self.path,
                data
                | {
                    "aanvraag_zaak_urn": f"maykin:abc:ztc:zaakabc:{data['aanvraag_zaak_urn'].rsplit(':', 1)[1]}"
                },
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["de urn en url mappings komen niet overeen"]},
            )

        with self.subTest("mapping correct"):
            response = self.client.post(self.path, data)
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, response.data
            )

            self.assertEqual(
                response.data["aanvraag_zaak_urn"],
                "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            )
            self.assertEqual(
                response.data["aanvraag_zaak_url"],
                "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            )

            product = Product.objects.get(uuid=response.data["uuid"])
            self.assertEqual(
                product.aanvraag_zaak_urn,
                "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            )
            self.assertEqual(
                product.aanvraag_zaak_url,
                "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
            )

        with self.subTest("different urn in mapping"):
            response = self.client.post(
                self.path,
                data
                | {
                    "aanvraag_zaak_urn": f"maykin:abc:ztc:zaakdef:{data['aanvraag_zaak_urn'].rsplit(':', 1)[1]}"
                },
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["de urn in de url mapping is niet hetzelfde"]},
            )

        with self.subTest("different url in mapping"):
            response = self.client.post(
                self.path,
                data
                | {
                    "aanvraag_zaak_url": f"https://maykin.ztc.com/zakendef/{data['aanvraag_zaak_url'].rsplit('/', 1)[1]}"
                },
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"aanvraag_zaak": ["de url in de urn mapping is niet hetzelfde"]},
            )

    def test_create_product_with_urn_and_url_no_mapping(self):
        data = self.data | {
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "aanvraag_zaak_url": "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UrnMappingConfig.objects.count(), 1)

        self.assertEqual(
            response.data["aanvraag_zaak_urn"],
            "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        self.assertEqual(
            response.data["aanvraag_zaak_url"],
            "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

        product = Product.objects.get(uuid=response.data["uuid"])
        self.assertEqual(
            product.aanvraag_zaak_urn,
            "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        self.assertEqual(
            product.aanvraag_zaak_url,
            "https://maykin.ztc.com/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
