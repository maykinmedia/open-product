import datetime
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from reversion.models import Version

from openproduct.locaties.tests.factories import (
    ContactFactory,
    LocatieFactory,
    OrganisatieFactory,
)
from openproduct.logging.constants import Events
from openproduct.logging.models import TimelineLogProxy
from openproduct.producttypen.models import (
    ExterneCode,
    ExterneVerwijzingConfig,
    Link,
    Parameter,
    Proces,
    ProductType,
    VerzoekType,
    ZaakType,
)
from openproduct.producttypen.tests.factories import (
    BestandFactory,
    ContentElementFactory,
    ExterneCodeFactory,
    JsonSchemaFactory,
    LinkFactory,
    ParameterFactory,
    PrijsFactory,
    PrijsOptieFactory,
    PrijsRegelFactory,
    ProcesFactory,
    ProductTypeFactory,
    ThemaFactory,
    UniformeProductNaamFactory,
    VerzoekTypeFactory,
    ZaakTypeFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


class TestProducttypeViewSet(BaseApiTestCase):
    path = reverse_lazy("producttype-list")

    def setUp(self):
        super().setUp()
        upn = UniformeProductNaamFactory.create()
        self.thema = ThemaFactory()

        self.data = {
            "naam": "test-producttype",
            "code": "PT-12345",
            "samenvatting": "test",
            "uniforme_product_naam": upn.naam,
            "thema_uuids": [self.thema.uuid],
        }

        config_patch = patch(
            "openproduct.producttypen.models.ExterneVerwijzingConfig.get_solo",
            return_value=ExterneVerwijzingConfig(
                zaaktypen_url="https://gemeente-a.zgw.nl/zaaktypen",
                verzoektypen_url="https://gemeente-a.zgw.nl/verzoektypen",
                processen_url="https://gemeente-a.zgw.nl/processen",
            ),
        )

        self.config_mock = config_patch.start()
        self.addCleanup(config_patch.stop)

    def detail_path(self, producttype):
        return reverse("producttype-detail", args=[producttype.uuid])

    def test_read_producttype_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "uniforme_product_naam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "naam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "thema_uuids": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "samenvatting": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "code": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_minimal_producttype(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        producttype = ProductType.objects.first()
        thema = producttype.themas.first()
        expected_data = {
            "uuid": str(producttype.uuid),
            "naam": producttype.naam,
            "code": producttype.code,
            "samenvatting": producttype.samenvatting,
            "interne_opmerkingen": producttype.interne_opmerkingen,
            "taal": "nl",
            "uniforme_product_naam": producttype.uniforme_product_naam.naam,
            "toegestane_statussen": [],
            "verbruiksobject_schema": None,
            "dataobject_schema": None,
            "prijzen": [],
            "links": [],
            "acties": [],
            "bestanden": [],
            "locaties": [],
            "organisaties": [],
            "contacten": [],
            "externe_codes": [],
            "parameters": [],
            "zaaktypen": [],
            "verzoektypen": [],
            "processen": [],
            "gepubliceerd": False,
            "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
            "update_datum": producttype.update_datum.astimezone().isoformat(),
            "keywords": [],
            "themas": [
                {
                    "uuid": str(thema.uuid),
                    "naam": thema.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": thema.update_datum.astimezone().isoformat(),
                    "beschrijving": thema.beschrijving,
                    "hoofd_thema": thema.hoofd_thema,
                }
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_create_producttype_with_language_header(self):
        for i, header in enumerate(
            [{"Accept-Language": "en"}, {"Content-Language": "en"}]
        ):
            with self.subTest(f"{header} should set default language only"):
                unique_code = f"T-123-{i}"
                print("test-code", unique_code)
                data = self.data | {"code": unique_code}

                response = self.client.post(self.path, data, headers=header)

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.data["taal"], "nl")
                self.assertEqual(response.data["naam"], self.data["naam"])
                self.assertEqual(response.headers["Content-Language"], "nl")

                producttype = ProductType.objects.get(uuid=response.data["uuid"])
                producttype.set_current_language("nl")
                self.assertEqual(producttype.naam, self.data["naam"])

    def test_create_producttype_without_thema_returns_error(self):
        data = self.data.copy()
        data["thema_uuids"] = []
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_uuids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ],
            },
        )

    def test_create_producttype_with_location(self):
        locatie = LocatieFactory.create()

        data = self.data | {"locatie_uuids": [locatie.uuid]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locaties__naam", flat=True)),
            [locatie.naam],
        )

    def test_create_producttype_with_organisatie(self):
        organisatie = OrganisatieFactory.create()

        data = self.data | {"organisatie_uuids": [organisatie.uuid]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisaties__naam", flat=True)),
            [organisatie.naam],
        )

    def test_create_producttype_with_contact(self):
        contact = ContactFactory.create()

        data = self.data | {"contact_uuids": [contact.uuid]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacten__naam", flat=True)),
            [contact.naam],
        )

        # contact org is added in ProductType clean
        self.assertEqual(ProductType.objects.get().organisaties.count(), 1)

    def test_create_producttype_with_toegestane_statussen(self):
        response = self.client.post(
            self.path, self.data | {"toegestane_statussen": ["gereed"]}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(response.data["toegestane_statussen"], ["gereed"])

    def test_create_producttype_with_duplicate_externe_code_systemen_returns_error(
        self,
    ):
        data = self.data | {
            "externe_codes": [
                {"naam": "ISO", "code": "123"},
                {"naam": "ISO", "code": "123"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "externe_codes": [
                    ErrorDetail(
                        string=_(
                            "Er bestaat al een externe code met de naam ISO voor dit ProductType."
                        ),
                        code="unique",
                    )
                ]
            },
        )

    def test_create_producttype_with_duplicate_parameter_names_returns_error(
        self,
    ):
        data = self.data | {
            "parameters": [
                {"naam": "doelgroep", "waarde": "inwoners"},
                {"naam": "doelgroep", "waarde": "bedrijven"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "parameters": [
                    ErrorDetail(
                        string="Er bestaat al een parameter met de naam doelgroep voor dit ProductType.",
                        code="unique",
                    )
                ]
            },
        )

    def test_create_producttype_without_externe_verwijzingen_without_config(self):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_create_producttype_with_externe_verwijzingen_without_config_returns_error(
        self,
    ):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        data = self.data | {
            "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "zaaktypen": [
                    ErrorDetail(
                        string="De zaaktypen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
                "verzoektypen": [
                    ErrorDetail(
                        string="De verzoektypen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
                "processen": [
                    ErrorDetail(
                        string="De processen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
            },
        )

    def test_create_producttype_with_duplicate_zaaktype_uuids_returns_error(
        self,
    ):
        data = self.data | {
            "zaaktypen": [
                {"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"},
                {"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "zaaktypen": [
                    ErrorDetail(
                        string="Er bestaat al een zaaktype met de uuid 99a8bd4f-4144-4105-9850-e477628852fc voor dit ProductType.",
                        code="unique",
                    )
                ]
            },
        )

    def test_create_producttype_with_duplicate_verzoektype_uuids_returns_error(
        self,
    ):
        data = self.data | {
            "verzoektypen": [
                {"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"},
                {"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "verzoektypen": [
                    ErrorDetail(
                        string="Er bestaat al een verzoektype met de uuid 99a8bd4f-4144-4105-9850-e477628852fc voor dit ProductType.",
                        code="unique",
                    )
                ]
            },
        )

    def test_create_producttype_with_duplicate_proces_uuids_returns_error(
        self,
    ):
        data = self.data | {
            "processen": [
                {"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"},
                {"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"},
            ],
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "processen": [
                    ErrorDetail(
                        string="Er bestaat al een proces met de uuid 99a8bd4f-4144-4105-9850-e477628852fc voor dit ProductType.",
                        code="unique",
                    )
                ]
            },
        )

    def test_create_producttype_with_duplicate_uuids_returns_error(self):
        thema = ThemaFactory.create()

        locatie = LocatieFactory.create()

        data = self.data | {
            "thema_uuids": [thema.uuid, thema.uuid],
            "locatie_uuids": [locatie.uuid, locatie.uuid],
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(thema.uuid),
                        code="invalid",
                    )
                ],
                "locatie_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(locatie.uuid),
                        code="invalid",
                    )
                ],
            },
        )

    def test_create_complete_producttype(self):
        locatie = LocatieFactory.create()
        organisatie = OrganisatieFactory.create()
        contact = ContactFactory.create()
        schema = JsonSchemaFactory.create(
            naam="test",
            schema={
                "type": "object",
                "properties": {"uren": {"type": "number"}},
                "required": ["uren"],
            },
        )

        data = self.data | {
            "locatie_uuids": [locatie.uuid],
            "organisatie_uuids": [organisatie.uuid],
            "contact_uuids": [contact.uuid],
            "externe_codes": [{"naam": "ISO", "code": "123"}],
            "parameters": [{"naam": "doelgroep", "waarde": "inwoners"}],
            "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verbruiksobject_schema_naam": schema.naam,
            "dataobject_schema_naam": schema.naam,
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        producttype = ProductType.objects.first()
        thema = producttype.themas.first()

        expected_data = {
            "uuid": str(producttype.uuid),
            "naam": producttype.naam,
            "code": producttype.code,
            "samenvatting": producttype.samenvatting,
            "interne_opmerkingen": producttype.interne_opmerkingen,
            "taal": "nl",
            "uniforme_product_naam": producttype.uniforme_product_naam.naam,
            "verbruiksobject_schema": {
                "naam": "test",
                "schema": {
                    "type": "object",
                    "properties": {"uren": {"type": "number"}},
                    "required": ["uren"],
                },
            },
            "dataobject_schema": {
                "naam": "test",
                "schema": {
                    "type": "object",
                    "properties": {"uren": {"type": "number"}},
                    "required": ["uren"],
                },
            },
            "toegestane_statussen": [],
            "prijzen": [],
            "links": [],
            "acties": [],
            "bestanden": [],
            "locaties": [
                {
                    "uuid": str(locatie.uuid),
                    "naam": locatie.naam,
                    "email": locatie.email,
                    "telefoonnummer": locatie.telefoonnummer,
                    "straat": locatie.straat,
                    "huisnummer": locatie.huisnummer,
                    "postcode": locatie.postcode,
                    "stad": locatie.stad,
                }
            ],
            "organisaties": [
                {
                    "uuid": str(contact.organisatie.uuid),
                    "code": str(contact.organisatie.code),
                    "naam": contact.organisatie.naam,
                    "email": contact.organisatie.email,
                    "telefoonnummer": contact.organisatie.telefoonnummer,
                    "straat": contact.organisatie.straat,
                    "huisnummer": contact.organisatie.huisnummer,
                    "postcode": contact.organisatie.postcode,
                    "stad": contact.organisatie.stad,
                },
                {
                    "uuid": str(organisatie.uuid),
                    "code": str(organisatie.code),
                    "naam": organisatie.naam,
                    "email": organisatie.email,
                    "telefoonnummer": organisatie.telefoonnummer,
                    "straat": organisatie.straat,
                    "huisnummer": organisatie.huisnummer,
                    "postcode": organisatie.postcode,
                    "stad": organisatie.stad,
                },
            ],
            "contacten": [
                {
                    "uuid": str(contact.uuid),
                    "naam": contact.naam,
                    "email": contact.email,
                    "telefoonnummer": contact.telefoonnummer,
                    "rol": contact.rol,
                    "organisatie": {
                        "uuid": str(contact.organisatie.uuid),
                        "code": str(contact.organisatie.code),
                        "naam": contact.organisatie.naam,
                        "email": contact.organisatie.email,
                        "telefoonnummer": contact.organisatie.telefoonnummer,
                        "straat": contact.organisatie.straat,
                        "huisnummer": contact.organisatie.huisnummer,
                        "postcode": contact.organisatie.postcode,
                        "stad": contact.organisatie.stad,
                    },
                }
            ],
            "externe_codes": [{"naam": "ISO", "code": "123"}],
            "parameters": [{"naam": "doelgroep", "waarde": "inwoners"}],
            "zaaktypen": [
                {
                    "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
            "verzoektypen": [
                {
                    "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
            "processen": [
                {
                    "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
            "gepubliceerd": False,
            "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
            "update_datum": producttype.update_datum.astimezone().isoformat(),
            "keywords": [],
            "themas": [
                {
                    "uuid": str(thema.uuid),
                    "naam": thema.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": thema.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": thema.update_datum.astimezone().isoformat(),
                    "beschrijving": thema.beschrijving,
                    "hoofd_thema": thema.hoofd_thema,
                }
            ],
        }
        self.assertEqual(response.data, expected_data)

    def test_create_producttype_creates_log_and_history(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        producttype = ProductType.objects.get()

        log = TimelineLogProxy.objects.filter(
            content_type__exact=ContentType.objects.get_for_model(producttype).pk,
            object_id=producttype.pk,
        ).get()

        self.assertEqual(log.event, Events.create)
        self.assertEqual(Version.objects.get_for_object(producttype).count(), 1)

    def test_update_minimal_producttype(self):
        producttype = ProductTypeFactory.create()
        response = self.client.put(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_producttype_with_language_header(self):
        for i, header in enumerate(
            [{"Accept-Language": "en"}, {"Content-Language": "en"}]
        ):
            with self.subTest(f"{header} should set default language only"):
                producttype = ProductTypeFactory.create()
                unique_code = f"T-123-{i}"
                data = self.data | {"code": unique_code}

                response = self.client.put(
                    self.detail_path(producttype),
                    data,
                    headers=header,
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["taal"], "nl")
                self.assertEqual(response.data["naam"], self.data["naam"])
                self.assertEqual(response.headers["Content-Language"], "nl")

                producttype = ProductType.objects.get(uuid=response.data["uuid"])
                producttype.set_current_language("nl")
                self.assertEqual(producttype.naam, self.data["naam"])

    def test_update_producttype_with_thema(self):
        producttype = ProductTypeFactory.create()
        thema = ThemaFactory.create()

        data = self.data | {"thema_uuids": [thema.uuid]}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("themas__naam", flat=True)),
            [thema.naam],
        )

    def test_update_producttype_removing_thema(self):
        producttype = ProductTypeFactory.create()
        data = self.data | {"thema_uuids": []}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_uuids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ]
            },
        )

    def test_update_producttype_with_location(self):
        producttype = ProductTypeFactory.create()
        locatie = LocatieFactory.create()

        data = self.data | {"locatie_uuids": [locatie.uuid]}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locaties__naam", flat=True)),
            [locatie.naam],
        )

    def test_update_producttype_with_organisatie(self):
        producttype = ProductTypeFactory.create()
        organisatie = OrganisatieFactory.create()

        data = self.data | {"organisatie_uuids": [organisatie.uuid]}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisaties__naam", flat=True)),
            [organisatie.naam],
        )

    def test_update_producttype_with_contact(self):
        producttype = ProductTypeFactory.create()
        contact = ContactFactory.create()

        data = self.data | {"contact_uuids": [contact.uuid]}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacten__naam", flat=True)),
            [contact.naam],
        )

        # contact org is added in ProductType clean
        self.assertEqual(ProductType.objects.get().organisaties.count(), 1)

    def test_update_producttype_with_duplicate_uuids_returns_error(self):
        producttype = ProductTypeFactory.create()
        thema = ThemaFactory.create()
        locatie = LocatieFactory.create()

        data = self.data | {
            "thema_uuids": [thema.uuid, thema.uuid],
            "locatie_uuids": [locatie.uuid, locatie.uuid],
        }

        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(thema.uuid),
                        code="invalid",
                    )
                ],
                "locatie_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(locatie.uuid),
                        code="invalid",
                    )
                ],
            },
        )

    def test_update_producttype_with_externe_code(self):
        producttype = ProductTypeFactory.create()

        externe_codes = [{"naam": "ISO", "code": "123"}]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_producttype_with_externe_code_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        externe_code = ExterneCodeFactory.create(producttype=producttype)

        externe_codes = [{"naam": externe_code.naam, "code": "456"}]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_producttype_removing_externe_codes(self):
        producttype = ProductTypeFactory.create()
        ExterneCodeFactory.create(producttype=producttype)
        ExterneCodeFactory.create(producttype=producttype)

        externe_codes = []
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 0)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_producttype_existing_externe_codes_are_kept(self):
        producttype = ProductTypeFactory.create()
        ExterneCodeFactory.create(producttype=producttype)

        response = self.client.patch(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)

    def test_update_producttype_with_parameter(self):
        producttype = ProductTypeFactory.create()

        parameters = [{"naam": "doelgroep", "waarde": "inwoners"}]
        data = self.data | {"parameters": parameters}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_update_producttype_with_parameter_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        parameter = ParameterFactory.create(producttype=producttype)

        parameters = [{"naam": parameter.naam, "waarde": "test"}]
        data = self.data | {"parameters": parameters}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_update_producttype_removing_parameters(self):
        producttype = ProductTypeFactory.create()
        ParameterFactory.create(producttype=producttype)
        ParameterFactory.create(producttype=producttype)

        parameters = []
        data = self.data | {"parameters": parameters}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 0)
        self.assertEqual(response.data["parameters"], parameters)

    def test_update_producttype_existing_parameters_are_kept(self):
        producttype = ProductTypeFactory.create()
        ParameterFactory.create(producttype=producttype)

        response = self.client.put(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)

    def test_update_producttype_without_externe_verwijzingen_without_config(self):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        producttype = ProductTypeFactory.create()

        response = self.client.put(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_producttype_with_externe_verwijzingen_without_config_returns_error(
        self,
    ):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        producttype = ProductTypeFactory.create()

        data = self.data | {
            "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
        }
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "zaaktypen": [
                    ErrorDetail(
                        string="De zaaktypen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
                "verzoektypen": [
                    ErrorDetail(
                        string="De verzoektypen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
                "processen": [
                    ErrorDetail(
                        string="De processen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
            },
        )

    def test_update_producttype_with_zaaktype(self):
        producttype = ProductTypeFactory.create()

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"zaaktypen": zaaktypen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)
        self.assertEqual(
            response.data["zaaktypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_update_producttype_with_zaaktype_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        ZaakTypeFactory.create(producttype=producttype)

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"zaaktypen": zaaktypen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)
        self.assertEqual(
            response.data["zaaktypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_update_producttype_removing_zaaktypen(self):
        producttype = ProductTypeFactory.create()
        ZaakTypeFactory.create(producttype=producttype)
        ZaakTypeFactory.create(producttype=producttype)

        zaaktypen = []
        data = self.data | {"zaaktypen": zaaktypen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 0)
        self.assertEqual(response.data["zaaktypen"], zaaktypen)

    def test_update_producttype_existing_zaaktypen_are_kept(self):
        producttype = ProductTypeFactory.create()
        ZaakTypeFactory.create(producttype=producttype)

        response = self.client.put(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)

    def test_update_producttype_with_verzoektype(self):
        producttype = ProductTypeFactory.create()

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"verzoektypen": verzoektypen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)
        self.assertEqual(
            response.data["verzoektypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_update_producttype_with_verzoektype_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        VerzoekTypeFactory.create(producttype=producttype)

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"verzoektypen": verzoektypen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)
        self.assertEqual(
            response.data["verzoektypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_update_producttype_removing_verzoektypen(self):
        producttype = ProductTypeFactory.create()
        VerzoekTypeFactory.create(producttype=producttype)
        VerzoekTypeFactory.create(producttype=producttype)

        verzoektypen = []
        data = self.data | {"verzoektypen": verzoektypen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(response.data["verzoektypen"], verzoektypen)

    def test_update_producttype_existing_verzoektypen_are_kept(self):
        producttype = ProductTypeFactory.create()
        VerzoekTypeFactory.create(producttype=producttype)

        response = self.client.put(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)

    def test_update_producttype_with_proces(self):
        producttype = ProductTypeFactory.create()

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"processen": processen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)
        self.assertEqual(
            response.data["processen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_update_producttype_with_proces_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        ProcesFactory.create(producttype=producttype)

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"processen": processen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)
        self.assertEqual(
            response.data["processen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_update_producttype_removing_processen(self):
        producttype = ProductTypeFactory.create()
        ProcesFactory.create(producttype=producttype)
        ProcesFactory.create(producttype=producttype)

        processen = []
        data = self.data | {"processen": processen}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 0)
        self.assertEqual(response.data["processen"], processen)

    def test_update_producttype_existing_processen_are_kept(self):
        producttype = ProductTypeFactory.create()
        ProcesFactory.create(producttype=producttype)

        response = self.client.put(self.detail_path(producttype), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)

    def test_update_producttype_creates_log_and_history(self):
        producttype = ProductTypeFactory.create()

        data = self.data | {"naam": "test123"}
        response = self.client.put(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

        log = TimelineLogProxy.objects.filter(
            content_type__exact=ContentType.objects.get_for_model(producttype).pk,
            object_id=producttype.pk,
        ).get()

        self.assertEqual(log.event, Events.update)
        # version is not created with factoryboy
        self.assertEqual(Version.objects.get_for_object(producttype).count(), 1)

    def test_partial_update_producttype(self):
        producttype = ProductTypeFactory.create()
        locatie = LocatieFactory.create()

        producttype.locaties.add(locatie)
        producttype.save()

        data = {"naam": "update"}

        response = self.client.patch(self.detail_path(producttype), data)
        producttype.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(producttype.locaties.count(), 1)
        self.assertEqual(producttype.naam, "update")

    def test_partial_update_producttype_with_duplicate_uuids_returns_error(self):
        producttype = ProductTypeFactory.create()
        thema = ThemaFactory.create()

        data = {
            "thema_uuids": [thema.uuid, thema.uuid],
        }

        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_uuids": [
                    ErrorDetail(
                        string=_("Dubbel uuid: {} op index 1.").format(thema.uuid),
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_producttype_removing_thema(self):
        producttype = ProductTypeFactory.create()
        data = {"thema_uuids": []}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_uuids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ]
            },
        )

    def test_partial_update_producttype_with_externe_code(self):
        producttype = ProductTypeFactory.create()

        externe_codes = [{"naam": "ISO", "code": "123"}]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_producttype_with_externe_code_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        externe_code = ExterneCodeFactory.create(producttype=producttype)

        externe_codes = [{"naam": externe_code.naam, "code": "456"}]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_producttype_removing_externe_codes(self):
        producttype = ProductTypeFactory.create()
        ExterneCodeFactory.create(producttype=producttype)
        ExterneCodeFactory.create(producttype=producttype)

        externe_codes = []
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 0)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_producttype_existing_externe_codes_are_kept(self):
        producttype = ProductTypeFactory.create()
        ExterneCodeFactory.create(producttype=producttype)

        response = self.client.patch(self.detail_path(producttype), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)

    def test_partial_update_producttype_with_parameter(self):
        producttype = ProductTypeFactory.create()

        parameters = [{"naam": "doelgroep", "waarde": "inwoners"}]
        data = {"parameters": parameters}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_partial_update_producttype_with_parameter_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        parameter = ParameterFactory.create(producttype=producttype)

        parameters = [{"naam": parameter.naam, "waarde": "test"}]
        data = {"parameters": parameters}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_partial_update_producttype_removing_parameters(self):
        producttype = ProductTypeFactory.create()
        ParameterFactory.create(producttype=producttype)
        ParameterFactory.create(producttype=producttype)

        parameters = []
        data = {"parameters": parameters}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 0)
        self.assertEqual(response.data["parameters"], parameters)

    def test_partial_update_producttype_existing_parameters_are_kept(self):
        producttype = ProductTypeFactory.create()
        ParameterFactory.create(producttype=producttype)

        response = self.client.patch(self.detail_path(producttype), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)

    def test_partial_update_producttype_without_externe_verwijzingen_without_config(
        self,
    ):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        producttype = ProductTypeFactory.create()

        response = self.client.patch(self.detail_path(producttype), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_partial_update_producttype_with_externe_verwijzingen_without_config_returns_error(
        self,
    ):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        producttype = ProductTypeFactory.create()

        data = self.data | {
            "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
        }
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "zaaktypen": [
                    ErrorDetail(
                        string="De zaaktypen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
                "verzoektypen": [
                    ErrorDetail(
                        string="De verzoektypen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
                "processen": [
                    ErrorDetail(
                        string="De processen url is niet geconfigureerd in de externe verwijzing config",
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_producttype_with_zaaktype(self):
        producttype = ProductTypeFactory.create()

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"zaaktypen": zaaktypen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)
        self.assertEqual(
            response.data["zaaktypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_partial_update_producttype_with_zaaktype_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        ZaakTypeFactory.create(producttype=producttype)

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"zaaktypen": zaaktypen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)
        self.assertEqual(
            response.data["zaaktypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_partial_update_producttype_removing_zaaktypen(self):
        producttype = ProductTypeFactory.create()
        ZaakTypeFactory.create(producttype=producttype)
        ZaakTypeFactory.create(producttype=producttype)

        zaaktypen = []
        data = {"zaaktypen": zaaktypen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 0)
        self.assertEqual(response.data["zaaktypen"], zaaktypen)

    def test_partial_update_producttype_existing_zaaktypen_are_kept(self):
        producttype = ProductTypeFactory.create()
        ZaakTypeFactory.create(producttype=producttype)

        response = self.client.patch(self.detail_path(producttype), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)

    def test_partial_update_producttype_with_verzoektype(self):
        producttype = ProductTypeFactory.create()

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"verzoektypen": verzoektypen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)
        self.assertEqual(
            response.data["verzoektypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_partial_update_producttype_with_verzoektype_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        VerzoekTypeFactory.create(producttype=producttype)

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"verzoektypen": verzoektypen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)
        self.assertEqual(
            response.data["verzoektypen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_partial_update_producttype_removing_verzoektypen(self):
        producttype = ProductTypeFactory.create()
        VerzoekTypeFactory.create(producttype=producttype)
        VerzoekTypeFactory.create(producttype=producttype)

        verzoektypen = []
        data = {"verzoektypen": verzoektypen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(response.data["verzoektypen"], verzoektypen)

    def test_partial_update_producttype_existing_verzoektypen_are_kept(self):
        producttype = ProductTypeFactory.create()
        VerzoekTypeFactory.create(producttype=producttype)

        response = self.client.patch(self.detail_path(producttype), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)

    def test_partial_update_producttype_with_proces(self):
        producttype = ProductTypeFactory.create()

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"processen": processen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)
        self.assertEqual(
            response.data["processen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_partial_update_producttype_with_proces_replacing_existing(self):
        producttype = ProductTypeFactory.create()
        ProcesFactory.create(producttype=producttype)

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"processen": processen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)
        self.assertEqual(
            response.data["processen"],
            [
                {
                    "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc"
                }
            ],
        )

    def test_partial_update_producttype_removing_processen(self):
        producttype = ProductTypeFactory.create()
        ProcesFactory.create(producttype=producttype)
        ProcesFactory.create(producttype=producttype)

        processen = []
        data = {"processen": processen}
        response = self.client.patch(self.detail_path(producttype), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 0)
        self.assertEqual(response.data["processen"], processen)

    def test_partial_update_producttype_existing_processen_are_kept(self):
        producttype = ProductTypeFactory.create()
        ProcesFactory.create(producttype=producttype)

        response = self.client.patch(self.detail_path(producttype), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)

    def test_read_producttype_link(self):
        producttype = ProductTypeFactory.create()
        link = LinkFactory.create(producttype=producttype)

        response = self.client.get(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "uuid": str(link.uuid),
                "naam": link.naam,
                "url": link.url,
            }
        ]

        self.assertEqual(response.data["links"], expected_data)

    def test_read_producttype_bestand(self):
        producttype = ProductTypeFactory.create()
        bestand = BestandFactory.create(producttype=producttype)

        response = self.client.get(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "uuid": str(bestand.uuid),
                "bestand": "http://testserver" + bestand.bestand.url,
            }
        ]
        self.assertEqual(response.data["bestanden"], expected_data)

    def test_read_producttype_prijs(self):
        producttype = ProductTypeFactory.create()
        prijs = PrijsFactory.create(producttype=producttype)
        prijs_optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "uuid": str(prijs.uuid),
                "actief_vanaf": str(prijs.actief_vanaf),
                "prijsopties": [
                    {
                        "uuid": str(prijs_optie.uuid),
                        "bedrag": str(prijs_optie.bedrag),
                        "beschrijving": prijs_optie.beschrijving,
                    }
                ],
                "prijsregels": [],
            }
        ]
        self.assertEqual(response.data["prijzen"], expected_data)

    def test_read_externe_verwijzingen_without_config(self):
        self.config_mock.return_value = ExterneVerwijzingConfig(
            zaaktypen_url="", verzoektypen_url="", processen_url=""
        )

        producttype = ProductTypeFactory.create()
        zaaktype = ZaakTypeFactory(producttype=producttype)
        verzoektype = VerzoekTypeFactory(producttype=producttype)
        proces = ProcesFactory(producttype=producttype)

        response = self.client.get(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zaaktypen"], [{"url": f"/{zaaktype.uuid}"}])
        self.assertEqual(
            response.data["verzoektypen"], [{"url": f"/{verzoektype.uuid}"}]
        )
        self.assertEqual(response.data["processen"], [{"url": f"/{proces.uuid}"}])

    def test_read_producttypen(self):
        producttype1 = ProductTypeFactory.create()
        producttype1.themas.add(self.thema)
        producttype1.save()

        producttype2 = ProductTypeFactory.create()
        producttype2.themas.add(self.thema)
        producttype2.save()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 2)
        expected_data = [
            {
                "uuid": str(producttype1.uuid),
                "naam": producttype1.naam,
                "code": producttype1.code,
                "samenvatting": producttype1.samenvatting,
                "interne_opmerkingen": producttype1.interne_opmerkingen,
                "taal": "nl",
                "uniforme_product_naam": producttype1.uniforme_product_naam.naam,
                "toegestane_statussen": [],
                "verbruiksobject_schema": None,
                "dataobject_schema": None,
                "prijzen": [],
                "links": [],
                "acties": [],
                "bestanden": [],
                "locaties": [],
                "organisaties": [],
                "contacten": [],
                "externe_codes": [],
                "parameters": [],
                "zaaktypen": [],
                "verzoektypen": [],
                "processen": [],
                "gepubliceerd": True,
                "aanmaak_datum": producttype1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype1.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "uuid": str(self.thema.uuid),
                        "naam": self.thema.naam,
                        "gepubliceerd": True,
                        "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": self.thema.update_datum.astimezone().isoformat(),
                        "beschrijving": self.thema.beschrijving,
                        "hoofd_thema": self.thema.hoofd_thema,
                    }
                ],
            },
            {
                "uuid": str(producttype2.uuid),
                "naam": producttype2.naam,
                "code": producttype2.code,
                "samenvatting": producttype2.samenvatting,
                "interne_opmerkingen": producttype2.interne_opmerkingen,
                "taal": "nl",
                "uniforme_product_naam": producttype2.uniforme_product_naam.naam,
                "toegestane_statussen": [],
                "verbruiksobject_schema": None,
                "dataobject_schema": None,
                "prijzen": [],
                "links": [],
                "acties": [],
                "bestanden": [],
                "locaties": [],
                "organisaties": [],
                "contacten": [],
                "externe_codes": [],
                "parameters": [],
                "zaaktypen": [],
                "verzoektypen": [],
                "processen": [],
                "gepubliceerd": True,
                "aanmaak_datum": producttype2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": producttype2.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "uuid": str(self.thema.uuid),
                        "naam": self.thema.naam,
                        "gepubliceerd": True,
                        "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                        "update_datum": self.thema.update_datum.astimezone().isoformat(),
                        "beschrijving": self.thema.beschrijving,
                        "hoofd_thema": self.thema.hoofd_thema,
                    }
                ],
            },
        ]
        self.assertCountEqual(response.data["resultaten"], expected_data)

    def test_read_producttype(self):
        producttype = ProductTypeFactory.create()
        producttype.themas.add(self.thema)
        producttype.save()

        response = self.client.get(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "uuid": str(producttype.uuid),
            "naam": producttype.naam,
            "code": producttype.code,
            "samenvatting": producttype.samenvatting,
            "interne_opmerkingen": producttype.interne_opmerkingen,
            "taal": "nl",
            "uniforme_product_naam": producttype.uniforme_product_naam.naam,
            "toegestane_statussen": [],
            "verbruiksobject_schema": None,
            "dataobject_schema": None,
            "prijzen": [],
            "links": [],
            "acties": [],
            "bestanden": [],
            "gepubliceerd": True,
            "aanmaak_datum": producttype.aanmaak_datum.astimezone().isoformat(),
            "update_datum": producttype.update_datum.astimezone().isoformat(),
            "keywords": [],
            "locaties": [],
            "organisaties": [],
            "contacten": [],
            "externe_codes": [],
            "parameters": [],
            "zaaktypen": [],
            "verzoektypen": [],
            "processen": [],
            "themas": [
                {
                    "uuid": str(self.thema.uuid),
                    "naam": self.thema.naam,
                    "gepubliceerd": True,
                    "aanmaak_datum": self.thema.aanmaak_datum.astimezone().isoformat(),
                    "update_datum": self.thema.update_datum.astimezone().isoformat(),
                    "beschrijving": self.thema.beschrijving,
                    "hoofd_thema": self.thema.hoofd_thema,
                }
            ],
        }

        self.assertEqual(response.data, expected_data)

    def test_read_producttype_in_other_language(self):
        producttype = ProductTypeFactory.create()
        producttype.themas.add(self.thema)
        producttype.set_current_language("en")
        producttype.naam = "producttype EN"
        producttype.samenvatting = "summary"
        producttype.save()

        response = self.client.get(
            self.detail_path(producttype), headers={"Accept-Language": "en"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["naam"], "producttype EN")
        self.assertEqual(response.data["samenvatting"], "summary")
        self.assertEqual(response.data["taal"], "en")

    def test_read_producttype_in_fallback_language(self):
        producttype = ProductTypeFactory.create(
            naam="producttype NL", samenvatting="samenvatting"
        )
        producttype.themas.add(self.thema)
        producttype.save()

        response = self.client.get(
            self.detail_path(producttype), headers={"Accept-Language": "de"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["naam"], "producttype NL")
        self.assertEqual(response.data["samenvatting"], "samenvatting")
        self.assertEqual(response.data["taal"], "nl")

    def test_delete_producttype(self):
        producttype = ProductTypeFactory.create()

        LinkFactory.create(producttype=producttype)

        response = self.client.delete(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductType.objects.count(), 0)
        self.assertEqual(Link.objects.count(), 0)

    def test_delete_producttype_creates_log(self):
        producttype = ProductTypeFactory.create()
        response = self.client.delete(self.detail_path(producttype))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductType.objects.count(), 0)

        log = TimelineLogProxy.objects.filter(
            content_type__exact=ContentType.objects.get_for_model(producttype).pk,
            object_id=producttype.pk,
        ).get()

        self.assertEqual(log.event, Events.delete)


@freeze_time("2024-01-01")
class TestProductTypeActions(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.producttype = ProductTypeFactory.create()
        self.list_path = reverse("producttype-actuele-prijzen")
        self.detail_path = reverse(
            "producttype-actuele-prijs", args=(self.producttype.uuid,)
        )

        self.expected_data = {
            "uuid": str(self.producttype.uuid),
            "code": self.producttype.code,
            "upl_naam": self.producttype.uniforme_product_naam.naam,
            "upl_uri": self.producttype.uniforme_product_naam.uri,
            "actuele_prijs": None,
        }

    def test_get_actuele_prijzen_when_producttype_has_no_prijzen(self):
        response = self.client.get(self.list_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data,
            ],
        )

    def test_get_actuele_prijs_when_producttype_has_no_prijzen(self):
        response = self.client.get(self.detail_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            self.expected_data,
        )

    def test_get_actuele_prijzen_when_producttype_only_has_prijs_in_future(self):
        PrijsFactory.create(
            producttype=self.producttype, actief_vanaf=datetime.date(2024, 2, 2)
        )

        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data,
            ],
        )

    def test_get_actuele_prijzen_when_producttype_has_prijsregels(self):
        prijs = PrijsFactory.create(
            producttype=self.producttype,
            actief_vanaf=datetime.date(2024, 1, 1),
        )

        optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data
                | {
                    "actuele_prijs": {
                        "uuid": str(prijs.uuid),
                        "actief_vanaf": "2024-01-01",
                        "prijsopties": [
                            {
                                "bedrag": str(optie.bedrag),
                                "beschrijving": optie.beschrijving,
                                "uuid": str(optie.uuid),
                            }
                        ],
                        "prijsregels": [],
                    },
                },
            ],
        )

    def test_get_actuele_prijzen_when_producttype_has_actuele_prijs(self):
        prijs = PrijsFactory.create(
            producttype=self.producttype,
            actief_vanaf=datetime.date(2024, 1, 1),
        )

        regel = PrijsRegelFactory.create(prijs=prijs)

        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data
                | {
                    "actuele_prijs": {
                        "uuid": str(prijs.uuid),
                        "actief_vanaf": "2024-01-01",
                        "prijsregels": [
                            {
                                "url": regel.url,
                                "beschrijving": regel.beschrijving,
                                "uuid": str(regel.uuid),
                                "mapping": regel.mapping,
                            }
                        ],
                        "prijsopties": [],
                    },
                },
            ],
        )

    def test_get_actuele_prijs_when_producttype_has_prijsopties(self):
        prijs = PrijsFactory.create(
            producttype=self.producttype,
            actief_vanaf=datetime.date(2024, 1, 1),
        )

        optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            self.expected_data
            | {
                "actuele_prijs": {
                    "uuid": str(prijs.uuid),
                    "actief_vanaf": "2024-01-01",
                    "prijsopties": [
                        {
                            "bedrag": str(optie.bedrag),
                            "beschrijving": optie.beschrijving,
                            "uuid": str(optie.uuid),
                        }
                    ],
                    "prijsregels": [],
                },
            },
        )

    def test_get_actuele_prijs_when_producttype_has_prijsregels(self):
        prijs = PrijsFactory.create(
            producttype=self.producttype,
            actief_vanaf=datetime.date(2024, 1, 1),
        )

        regel = PrijsRegelFactory.create(prijs=prijs)

        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            self.expected_data
            | {
                "actuele_prijs": {
                    "uuid": str(prijs.uuid),
                    "actief_vanaf": "2024-01-01",
                    "prijsregels": [
                        {
                            "url": regel.url,
                            "beschrijving": regel.beschrijving,
                            "uuid": str(regel.uuid),
                            "mapping": regel.mapping,
                        }
                    ],
                    "prijsopties": [],
                },
            },
        )

    def test_put_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "en"))

        data = {"naam": "name EN", "samenvatting": "summary EN"}
        response = self.client.put(path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "uuid": str(self.producttype.uuid),
                "naam": "name EN",
                "samenvatting": "summary EN",
            },
        )
        self.producttype.set_current_language("en")
        self.assertEqual(self.producttype.naam, "name EN")

        self.producttype.set_current_language("nl")
        self.assertNotEqual(self.producttype.naam, "name EN")

    def test_put_nl_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "nl"))

        data = {"naam": "name NL", "samenvatting": "summary NL"}
        response = self.client.put(path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_vertaling_with_unsupported_language(self):
        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "fr"))

        data = {"naam": "name FR", "samenvatting": "summary FR"}
        response = self.client.put(path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_vertaling(self):
        self.producttype.set_current_language("en")
        self.producttype.naam = "name EN"
        self.producttype.samenvatting = "summary EN"
        self.producttype.save()

        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "en"))

        data = {"naam": "name EN 2"}
        response = self.client.patch(path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producttype.refresh_from_db()
        self.assertEqual(self.producttype.naam, "name EN 2")

    def test_delete_nonexistent_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "en"))

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nl_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "nl"))

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_vertaling(self):
        self.producttype.set_current_language("en")
        self.producttype.naam = "name EN"
        self.producttype.samenvatting = "summary EN"
        self.producttype.save()

        path = reverse("producttype-vertaling", args=(self.producttype.uuid, "en"))

        response = self.client.delete(path)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.producttype.refresh_from_db()
        self.assertFalse(self.producttype.has_translation("en"))

    def test_nl_content(self):
        element1 = ContentElementFactory.create(producttype=self.producttype)
        element2 = ContentElementFactory.create(producttype=self.producttype)

        path = reverse("producttype-content", args=(self.producttype.uuid,))
        response = self.client.get(path, headers={"Accept-Language": "nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertCountEqual(
            response.data,
            [
                {
                    "uuid": str(element1.uuid),
                    "taal": "nl",
                    "content": element1.content,
                    "labels": [],
                },
                {
                    "uuid": str(element2.uuid),
                    "taal": "nl",
                    "content": element2.content,
                    "labels": [],
                },
            ],
        )

    def test_en_content_and_fallback(self):
        element1 = ContentElementFactory.create(producttype=self.producttype)
        element1.set_current_language("en")
        element1.content = "EN content"
        element1.save()

        element2 = ContentElementFactory.create(producttype=self.producttype)

        path = reverse("producttype-content", args=(self.producttype.uuid,))
        response = self.client.get(path, headers={"Accept-Language": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertCountEqual(
            response.data,
            [
                {
                    "uuid": str(element1.uuid),
                    "taal": "en",
                    "content": "EN content",
                    "labels": [],
                },
                {
                    "uuid": str(element2.uuid),
                    "taal": "nl",
                    "content": element2.content,
                    "labels": [],
                },
            ],
        )
