import datetime

from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.locaties.tests.factories import (
    ContactFactory,
    LocatieFactory,
    OrganisatieFactory,
)
from open_producten.producttypen.models import (
    ExterneCode,
    ExterneVerwijzingConfig,
    Link,
    Parameter,
    Proces,
    ProductType,
    VerzoekType,
    ZaakType,
)
from open_producten.producttypen.tests.factories import (
    BestandFactory,
    ContentElementFactory,
    ExterneCodeFactory,
    JsonSchemaFactory,
    LinkFactory,
    ParameterFactory,
    PrijsFactory,
    PrijsOptieFactory,
    ProcesFactory,
    ProductTypeFactory,
    ThemaFactory,
    UniformeProductNaamFactory,
    VerzoekTypeFactory,
    ZaakTypeFactory,
)
from open_producten.utils.tests.cases import BaseApiTestCase


class TestProducttypeViewSet(BaseApiTestCase):
    path = reverse_lazy("producttype-list")

    def setUp(self):
        super().setUp()
        upn = UniformeProductNaamFactory.create()
        self.thema = ThemaFactory()

        self.data = {
            "naam": "test-product-type",
            "code": "PT=12345",
            "samenvatting": "test",
            "uniforme_product_naam": upn.naam,
            "thema_ids": [self.thema.id],
        }

        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = "https://gemeente-a.zgw.nl/zaaktypen"
        config.verzoektypen_url = "https://gemeente-a.zgw.nl/verzoektypen"
        config.processen_url = "https://gemeente-a.zgw.nl/processen"
        config.save()

    def detail_path(self, product_type):
        return reverse("producttype-detail", args=[product_type.id])

    def test_read_product_type_without_credentials_returns_error(self):
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
                "thema_ids": [
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

    def test_create_minimal_product_type(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

        product_type = ProductType.objects.first()
        thema = product_type.themas.first()
        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "code": product_type.code,
            "samenvatting": product_type.samenvatting,
            "interne_opmerkingen": product_type.interne_opmerkingen,
            "taal": "nl",
            "uniforme_product_naam": product_type.uniforme_product_naam.naam,
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
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "themas": [
                {
                    "id": str(thema.id),
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

    def test_create_product_type_without_thema_returns_error(self):
        data = self.data.copy()
        data["thema_ids"] = []
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ],
            },
        )

    def test_create_product_type_with_location(self):
        locatie = LocatieFactory.create()

        data = self.data | {"locatie_ids": [locatie.id]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locaties__naam", flat=True)),
            [locatie.naam],
        )

    def test_create_product_type_with_organisatie(self):
        organisatie = OrganisatieFactory.create()

        data = self.data | {"organisatie_ids": [organisatie.id]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisaties__naam", flat=True)),
            [organisatie.naam],
        )

    def test_create_product_type_with_contact(self):
        contact = ContactFactory.create()

        data = self.data | {"contact_ids": [contact.id]}
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacten__voornaam", flat=True)),
            [contact.voornaam],
        )

        # contact org is added in ProductType clean
        self.assertEqual(ProductType.objects.get().organisaties.count(), 1)

    def test_create_product_type_with_toegestane_statussen(self):
        response = self.client.post(
            self.path, self.data | {"toegestane_statussen": ["gereed"]}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(response.data["toegestane_statussen"], ["gereed"])

    def test_create_product_type_with_duplicate_externe_code_systemen_returns_error(
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

    def test_create_product_type_with_duplicate_parameter_names_returns_error(
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

    def test_create_product_type_without_externe_verwijzingen_without_config(self):
        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_create_product_type_with_externe_verwijzingen_without_config_returns_error(
        self,
    ):

        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

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

    def test_create_product_type_with_duplicate_zaaktype_uuids_returns_error(
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

    def test_create_product_type_with_duplicate_verzoektype_uuids_returns_error(
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

    def test_create_product_type_with_duplicate_proces_uuids_returns_error(
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

    def test_create_product_type_with_duplicate_ids_returns_error(self):
        thema = ThemaFactory.create()

        locatie = LocatieFactory.create()

        data = self.data | {
            "thema_ids": [thema.id, thema.id],
            "locatie_ids": [locatie.id, locatie.id],
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(thema.id),
                        code="invalid",
                    )
                ],
                "locatie_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(locatie.id),
                        code="invalid",
                    )
                ],
            },
        )

    def test_create_complete_product_type(self):

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
            "locatie_ids": [locatie.id],
            "organisatie_ids": [organisatie.id],
            "contact_ids": [contact.id],
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

        product_type = ProductType.objects.first()
        thema = product_type.themas.first()

        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "code": product_type.code,
            "samenvatting": product_type.samenvatting,
            "interne_opmerkingen": product_type.interne_opmerkingen,
            "taal": "nl",
            "uniforme_product_naam": product_type.uniforme_product_naam.naam,
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
                    "id": str(locatie.id),
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
                    "id": str(organisatie.id),
                    "code": str(organisatie.code),
                    "naam": organisatie.naam,
                    "email": organisatie.email,
                    "telefoonnummer": organisatie.telefoonnummer,
                    "straat": organisatie.straat,
                    "huisnummer": organisatie.huisnummer,
                    "postcode": organisatie.postcode,
                    "stad": organisatie.stad,
                },
                {
                    "id": str(contact.organisatie.id),
                    "code": str(contact.organisatie.code),
                    "naam": contact.organisatie.naam,
                    "email": contact.organisatie.email,
                    "telefoonnummer": contact.organisatie.telefoonnummer,
                    "straat": contact.organisatie.straat,
                    "huisnummer": contact.organisatie.huisnummer,
                    "postcode": contact.organisatie.postcode,
                    "stad": contact.organisatie.stad,
                },
            ],
            "contacten": [
                {
                    "id": str(contact.id),
                    "voornaam": contact.voornaam,
                    "achternaam": contact.achternaam,
                    "email": contact.email,
                    "telefoonnummer": contact.telefoonnummer,
                    "rol": contact.rol,
                    "organisatie": {
                        "id": str(contact.organisatie.id),
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
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
            "keywords": [],
            "themas": [
                {
                    "id": str(thema.id),
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

    def test_update_minimal_product_type(self):
        product_type = ProductTypeFactory.create()
        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_thema(self):
        product_type = ProductTypeFactory.create()
        thema = ThemaFactory.create()

        data = self.data | {"thema_ids": [thema.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("themas__naam", flat=True)),
            [thema.naam],
        )

    def test_update_product_type_removing_thema(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"thema_ids": []}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ]
            },
        )

    def test_update_product_type_with_location(self):
        product_type = ProductTypeFactory.create()
        locatie = LocatieFactory.create()

        data = self.data | {"locatie_ids": [locatie.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("locaties__naam", flat=True)),
            [locatie.naam],
        )

    def test_update_product_type_with_organisatie(self):
        product_type = ProductTypeFactory.create()
        organisatie = OrganisatieFactory.create()

        data = self.data | {"organisatie_ids": [organisatie.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("organisaties__naam", flat=True)),
            [organisatie.naam],
        )

    def test_update_product_type_with_contact(self):
        product_type = ProductTypeFactory.create()
        contact = ContactFactory.create()

        data = self.data | {"contact_ids": [contact.id]}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(
            list(ProductType.objects.values_list("contacten__voornaam", flat=True)),
            [contact.voornaam],
        )

        # contact org is added in ProductType clean
        self.assertEqual(ProductType.objects.get().organisaties.count(), 1)

    def test_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        thema = ThemaFactory.create()
        locatie = LocatieFactory.create()

        data = self.data | {
            "thema_ids": [thema.id, thema.id],
            "locatie_ids": [locatie.id, locatie.id],
        }

        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(thema.id),
                        code="invalid",
                    )
                ],
                "locatie_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(locatie.id),
                        code="invalid",
                    )
                ],
            },
        )

    def test_update_product_type_with_externe_code(self):
        product_type = ProductTypeFactory.create()

        externe_codes = [{"naam": "ISO", "code": "123"}]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_product_type_with_externe_code_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        externe_code = ExterneCodeFactory.create(product_type=product_type)

        externe_codes = [{"naam": externe_code.naam, "code": "456"}]
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_product_type_removing_externe_codes(self):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)

        externe_codes = []
        data = self.data | {"externe_codes": externe_codes}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 0)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_update_product_type_existing_externe_codes_are_kept(self):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)

    def test_update_product_type_with_parameter(self):
        product_type = ProductTypeFactory.create()

        parameters = [{"naam": "doelgroep", "waarde": "inwoners"}]
        data = self.data | {"parameters": parameters}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_update_product_type_with_parameter_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        parameter = ParameterFactory.create(product_type=product_type)

        parameters = [{"naam": parameter.naam, "waarde": "test"}]
        data = self.data | {"parameters": parameters}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_update_product_type_removing_parameters(self):
        product_type = ProductTypeFactory.create()
        ParameterFactory.create(product_type=product_type)
        ParameterFactory.create(product_type=product_type)

        parameters = []
        data = self.data | {"parameters": parameters}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 0)
        self.assertEqual(response.data["parameters"], parameters)

    def test_update_product_type_existing_parameters_are_kept(self):
        product_type = ProductTypeFactory.create()
        ParameterFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)

    def test_update_product_type_without_externe_verwijzingen_without_config(self):
        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

        product_type = ProductTypeFactory.create()

        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_update_product_type_with_externe_verwijzingen_without_config_returns_error(
        self,
    ):
        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

        product_type = ProductTypeFactory.create()

        data = self.data | {
            "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
        }
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_with_zaaktype(self):
        product_type = ProductTypeFactory.create()

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"zaaktypen": zaaktypen}
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_with_zaaktype_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        ZaakTypeFactory.create(product_type=product_type)

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"zaaktypen": zaaktypen}
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_removing_zaaktypen(self):
        product_type = ProductTypeFactory.create()
        ZaakTypeFactory.create(product_type=product_type)
        ZaakTypeFactory.create(product_type=product_type)

        zaaktypen = []
        data = self.data | {"zaaktypen": zaaktypen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 0)
        self.assertEqual(response.data["zaaktypen"], zaaktypen)

    def test_update_product_type_existing_zaaktypen_are_kept(self):
        product_type = ProductTypeFactory.create()
        ZaakTypeFactory.create(product_type=product_type)

        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)

    def test_update_product_type_with_verzoektype(self):
        product_type = ProductTypeFactory.create()

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"verzoektypen": verzoektypen}
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_with_verzoektype_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        VerzoekTypeFactory.create(product_type=product_type)

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"verzoektypen": verzoektypen}
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_removing_verzoektypen(self):
        product_type = ProductTypeFactory.create()
        VerzoekTypeFactory.create(product_type=product_type)
        VerzoekTypeFactory.create(product_type=product_type)

        verzoektypen = []
        data = self.data | {"verzoektypen": verzoektypen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(response.data["verzoektypen"], verzoektypen)

    def test_update_product_type_existing_verzoektypen_are_kept(self):
        product_type = ProductTypeFactory.create()
        VerzoekTypeFactory.create(product_type=product_type)

        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)

    def test_update_product_type_with_proces(self):
        product_type = ProductTypeFactory.create()

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"processen": processen}
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_with_proces_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        ProcesFactory.create(product_type=product_type)

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = self.data | {"processen": processen}
        response = self.client.put(self.detail_path(product_type), data)

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

    def test_update_product_type_removing_processen(self):
        product_type = ProductTypeFactory.create()
        ProcesFactory.create(product_type=product_type)
        ProcesFactory.create(product_type=product_type)

        processen = []
        data = self.data | {"processen": processen}
        response = self.client.put(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 0)
        self.assertEqual(response.data["processen"], processen)

    def test_update_product_type_existing_processen_are_kept(self):
        product_type = ProductTypeFactory.create()
        ProcesFactory.create(product_type=product_type)

        response = self.client.put(self.detail_path(product_type), self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)

    def test_partial_update_product_type(self):
        product_type = ProductTypeFactory.create()
        locatie = LocatieFactory.create()

        product_type.locaties.add(locatie)
        product_type.save()

        data = {"naam": "update"}

        response = self.client.patch(self.detail_path(product_type), data)
        product_type.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product_type.locaties.count(), 1)
        self.assertEqual(product_type.naam, "update")

    def test_partial_update_product_type_with_duplicate_ids_returns_error(self):
        product_type = ProductTypeFactory.create()
        thema = ThemaFactory.create()

        data = {
            "thema_ids": [thema.id, thema.id],
        }

        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(thema.id),
                        code="invalid",
                    )
                ],
            },
        )

    def test_partial_update_product_type_removing_thema(self):
        product_type = ProductTypeFactory.create()
        data = {"thema_ids": []}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "thema_ids": [
                    ErrorDetail(
                        string=_("Er is minimaal één thema vereist."), code="invalid"
                    )
                ]
            },
        )

    def test_partial_update_product_type_with_externe_code(self):
        product_type = ProductTypeFactory.create()

        externe_codes = [{"naam": "ISO", "code": "123"}]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_product_type_with_externe_code_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        externe_code = ExterneCodeFactory.create(product_type=product_type)

        externe_codes = [{"naam": externe_code.naam, "code": "456"}]
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_product_type_removing_externe_codes(self):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)
        ExterneCodeFactory.create(product_type=product_type)

        externe_codes = []
        data = {"externe_codes": externe_codes}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 0)
        self.assertEqual(response.data["externe_codes"], externe_codes)

    def test_partial_update_product_type_existing_externe_codes_are_kept(self):
        product_type = ProductTypeFactory.create()
        ExterneCodeFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExterneCode.objects.count(), 1)

    def test_partial_update_product_type_with_parameter(self):
        product_type = ProductTypeFactory.create()

        parameters = [{"naam": "doelgroep", "waarde": "inwoners"}]
        data = {"parameters": parameters}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_partial_update_product_type_with_parameter_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        parameter = ParameterFactory.create(product_type=product_type)

        parameters = [{"naam": parameter.naam, "waarde": "test"}]
        data = {"parameters": parameters}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)
        self.assertEqual(response.data["parameters"], parameters)

    def test_partial_update_product_type_removing_parameters(self):
        product_type = ProductTypeFactory.create()
        ParameterFactory.create(product_type=product_type)
        ParameterFactory.create(product_type=product_type)

        parameters = []
        data = {"parameters": parameters}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 0)
        self.assertEqual(response.data["parameters"], parameters)

    def test_partial_update_product_type_existing_parameters_are_kept(self):
        product_type = ProductTypeFactory.create()
        ParameterFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Parameter.objects.count(), 1)

    def test_partial_update_product_type_without_externe_verwijzingen_without_config(
        self,
    ):
        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

        product_type = ProductTypeFactory.create()

        response = self.client.patch(self.detail_path(product_type), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductType.objects.count(), 1)

    def test_partial_update_product_type_with_externe_verwijzingen_without_config_returns_error(
        self,
    ):
        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

        product_type = ProductTypeFactory.create()

        data = self.data | {
            "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
            "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
        }
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_with_zaaktype(self):
        product_type = ProductTypeFactory.create()

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"zaaktypen": zaaktypen}
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_with_zaaktype_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        ZaakTypeFactory.create(product_type=product_type)

        zaaktypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"zaaktypen": zaaktypen}
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_removing_zaaktypen(self):
        product_type = ProductTypeFactory.create()
        ZaakTypeFactory.create(product_type=product_type)
        ZaakTypeFactory.create(product_type=product_type)

        zaaktypen = []
        data = {"zaaktypen": zaaktypen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 0)
        self.assertEqual(response.data["zaaktypen"], zaaktypen)

    def test_partial_update_product_type_existing_zaaktypen_are_kept(self):
        product_type = ProductTypeFactory.create()
        ZaakTypeFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ZaakType.objects.count(), 1)

    def test_partial_update_product_type_with_verzoektype(self):
        product_type = ProductTypeFactory.create()

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"verzoektypen": verzoektypen}
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_with_verzoektype_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        VerzoekTypeFactory.create(product_type=product_type)

        verzoektypen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"verzoektypen": verzoektypen}
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_removing_verzoektypen(self):
        product_type = ProductTypeFactory.create()
        VerzoekTypeFactory.create(product_type=product_type)
        VerzoekTypeFactory.create(product_type=product_type)

        verzoektypen = []
        data = {"verzoektypen": verzoektypen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 0)
        self.assertEqual(response.data["verzoektypen"], verzoektypen)

    def test_partial_update_product_type_existing_verzoektypen_are_kept(self):
        product_type = ProductTypeFactory.create()
        VerzoekTypeFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerzoekType.objects.count(), 1)

    def test_partial_update_product_type_with_proces(self):
        product_type = ProductTypeFactory.create()

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"processen": processen}
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_with_proces_replacing_existing(self):
        product_type = ProductTypeFactory.create()
        ProcesFactory.create(product_type=product_type)

        processen = [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}]
        data = {"processen": processen}
        response = self.client.patch(self.detail_path(product_type), data)

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

    def test_partial_update_product_type_removing_processen(self):
        product_type = ProductTypeFactory.create()
        ProcesFactory.create(product_type=product_type)
        ProcesFactory.create(product_type=product_type)

        processen = []
        data = {"processen": processen}
        response = self.client.patch(self.detail_path(product_type), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 0)
        self.assertEqual(response.data["processen"], processen)

    def test_partial_update_product_type_existing_processen_are_kept(self):
        product_type = ProductTypeFactory.create()
        ProcesFactory.create(product_type=product_type)

        response = self.client.patch(self.detail_path(product_type), {"naam": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proces.objects.count(), 1)

    def test_read_product_type_link(self):
        product_type = ProductTypeFactory.create()
        link = LinkFactory.create(product_type=product_type)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(link.id),
                "naam": link.naam,
                "url": link.url,
            }
        ]

        self.assertEqual(response.data["links"], expected_data)

    def test_read_product_type_bestand(self):
        product_type = ProductTypeFactory.create()
        bestand = BestandFactory.create(product_type=product_type)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(bestand.id),
                "bestand": "http://testserver" + bestand.bestand.url,
            }
        ]
        self.assertEqual(response.data["bestanden"], expected_data)

    def test_read_product_type_prijs(self):
        product_type = ProductTypeFactory.create()
        prijs = PrijsFactory.create(product_type=product_type)
        prijs_optie = PrijsOptieFactory.create(prijs=prijs)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": str(prijs.id),
                "actief_vanaf": str(prijs.actief_vanaf),
                "prijsopties": [
                    {
                        "id": str(prijs_optie.id),
                        "bedrag": str(prijs_optie.bedrag),
                        "beschrijving": prijs_optie.beschrijving,
                    }
                ],
            }
        ]
        self.assertEqual(response.data["prijzen"], expected_data)

    def test_read_externe_verwijzingen_without_config(self):
        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = ""
        config.verzoektypen_url = ""
        config.processen_url = ""
        config.save()

        product_type = ProductTypeFactory.create()
        zaaktype = ZaakTypeFactory(product_type=product_type)
        verzoektype = VerzoekTypeFactory(product_type=product_type)
        proces = ProcesFactory(product_type=product_type)

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zaaktypen"], [{"url": f"/{zaaktype.uuid}"}])
        self.assertEqual(
            response.data["verzoektypen"], [{"url": f"/{verzoektype.uuid}"}]
        )
        self.assertEqual(response.data["processen"], [{"url": f"/{proces.uuid}"}])

    def test_read_product_typen(self):
        product_type1 = ProductTypeFactory.create()
        product_type1.themas.add(self.thema)
        product_type1.save()

        product_type2 = ProductTypeFactory.create()
        product_type2.themas.add(self.thema)
        product_type2.save()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(product_type1.id),
                "naam": product_type1.naam,
                "code": product_type1.code,
                "samenvatting": product_type1.samenvatting,
                "interne_opmerkingen": product_type1.interne_opmerkingen,
                "taal": "nl",
                "uniforme_product_naam": product_type1.uniforme_product_naam.naam,
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
                "aanmaak_datum": product_type1.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type1.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "id": str(self.thema.id),
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
                "id": str(product_type2.id),
                "naam": product_type2.naam,
                "code": product_type2.code,
                "samenvatting": product_type2.samenvatting,
                "interne_opmerkingen": product_type2.interne_opmerkingen,
                "taal": "nl",
                "uniforme_product_naam": product_type2.uniforme_product_naam.naam,
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
                "aanmaak_datum": product_type2.aanmaak_datum.astimezone().isoformat(),
                "update_datum": product_type2.update_datum.astimezone().isoformat(),
                "keywords": [],
                "themas": [
                    {
                        "id": str(self.thema.id),
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
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_product_type(self):
        product_type = ProductTypeFactory.create()
        product_type.themas.add(self.thema)
        product_type.save()

        response = self.client.get(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(product_type.id),
            "naam": product_type.naam,
            "code": product_type.code,
            "samenvatting": product_type.samenvatting,
            "interne_opmerkingen": product_type.interne_opmerkingen,
            "taal": "nl",
            "uniforme_product_naam": product_type.uniforme_product_naam.naam,
            "toegestane_statussen": [],
            "verbruiksobject_schema": None,
            "dataobject_schema": None,
            "prijzen": [],
            "links": [],
            "acties": [],
            "bestanden": [],
            "gepubliceerd": True,
            "aanmaak_datum": product_type.aanmaak_datum.astimezone().isoformat(),
            "update_datum": product_type.update_datum.astimezone().isoformat(),
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
                    "id": str(self.thema.id),
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

    def test_read_product_type_in_other_language(self):
        product_type = ProductTypeFactory.create()
        product_type.themas.add(self.thema)
        product_type.set_current_language("en")
        product_type.naam = "product type EN"
        product_type.samenvatting = "summary"
        product_type.save()

        response = self.client.get(
            self.detail_path(product_type), headers={"Accept-Language": "en"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["naam"], "product type EN")
        self.assertEqual(response.data["samenvatting"], "summary")
        self.assertEqual(response.data["taal"], "en")

    def test_read_product_type_in_fallback_language(self):
        product_type = ProductTypeFactory.create(
            naam="product type NL", samenvatting="samenvatting"
        )
        product_type.themas.add(self.thema)
        product_type.save()

        response = self.client.get(
            self.detail_path(product_type), headers={"Accept-Language": "de"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["naam"], "product type NL")
        self.assertEqual(response.data["samenvatting"], "samenvatting")
        self.assertEqual(response.data["taal"], "nl")

    def test_delete_product_type(self):
        product_type = ProductTypeFactory.create()

        LinkFactory.create(product_type=product_type)

        response = self.client.delete(self.detail_path(product_type))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductType.objects.count(), 0)
        self.assertEqual(Link.objects.count(), 0)


@freeze_time("2024-01-01")
class TestProductTypeActions(BaseApiTestCase):

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.list_path = reverse("producttype-actuele-prijzen")
        self.detail_path = reverse(
            "producttype-actuele-prijs", args=(self.product_type.id,)
        )

        self.expected_data = {
            "id": str(self.product_type.id),
            "code": self.product_type.code,
            "upl_naam": self.product_type.uniforme_product_naam.naam,
            "upl_uri": self.product_type.uniforme_product_naam.uri,
            "actuele_prijs": None,
        }

    def test_get_actuele_prijzen_when_product_type_has_no_prijzen(self):
        response = self.client.get(self.list_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data,
            ],
        )

    def test_get_actuele_prijs_when_product_type_has_no_prijzen(self):
        response = self.client.get(self.detail_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            self.expected_data,
        )

    def test_get_actuele_prijzen_when_product_type_only_has_prijs_in_future(self):
        PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 2, 2)
        )

        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                self.expected_data,
            ],
        )

    def test_get_actuele_prijzen_when_product_type_has_actuele_prijs(self):
        prijs = PrijsFactory.create(
            product_type=self.product_type,
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
                        "id": str(prijs.id),
                        "actief_vanaf": "2024-01-01",
                        "prijsopties": [
                            {
                                "bedrag": str(optie.bedrag),
                                "beschrijving": optie.beschrijving,
                                "id": str(optie.id),
                            }
                        ],
                    },
                },
            ],
        )

    def test_get_actuele_prijs_when_product_type_has_actuele_prijs(self):
        prijs = PrijsFactory.create(
            product_type=self.product_type,
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
                    "id": str(prijs.id),
                    "actief_vanaf": "2024-01-01",
                    "prijsopties": [
                        {
                            "bedrag": str(optie.bedrag),
                            "beschrijving": optie.beschrijving,
                            "id": str(optie.id),
                        }
                    ],
                },
            },
        )

    def test_put_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.product_type.id, "en"))

        data = {"naam": "name EN", "samenvatting": "summary EN"}
        response = self.client.put(path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": str(self.product_type.id),
                "naam": "name EN",
                "samenvatting": "summary EN",
            },
        )
        self.product_type.set_current_language("en")
        self.assertEqual(self.product_type.naam, "name EN")

        self.product_type.set_current_language("nl")
        self.assertNotEqual(self.product_type.naam, "name EN")

    def test_put_nl_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.product_type.id, "nl"))

        data = {"naam": "name NL", "samenvatting": "summary NL"}
        response = self.client.put(path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_vertaling_with_unsupported_language(self):
        path = reverse("producttype-vertaling", args=(self.product_type.id, "fr"))

        data = {"naam": "name FR", "samenvatting": "summary FR"}
        response = self.client.put(path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_vertaling(self):
        self.product_type.set_current_language("en")
        self.product_type.naam = "name EN"
        self.product_type.samenvatting = "summary EN"
        self.product_type.save()

        path = reverse("producttype-vertaling", args=(self.product_type.id, "en"))

        data = {"naam": "name EN 2"}
        response = self.client.patch(path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_type.refresh_from_db()
        self.assertEqual(self.product_type.naam, "name EN 2")

    def test_delete_nonexistent_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.product_type.id, "en"))

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nl_vertaling(self):
        path = reverse("producttype-vertaling", args=(self.product_type.id, "nl"))

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_vertaling(self):
        self.product_type.set_current_language("en")
        self.product_type.naam = "name EN"
        self.product_type.samenvatting = "summary EN"
        self.product_type.save()

        path = reverse("producttype-vertaling", args=(self.product_type.id, "en"))

        response = self.client.delete(path)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.product_type.refresh_from_db()
        self.assertFalse(self.product_type.has_translation("en"))

    def test_nl_content(self):
        element1 = ContentElementFactory.create(product_type=self.product_type)
        element2 = ContentElementFactory.create(product_type=self.product_type)

        path = reverse("producttype-content", args=(self.product_type.id,))
        response = self.client.get(path, headers={"Accept-Language": "nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertCountEqual(
            response.data,
            [
                {
                    "id": str(element1.id),
                    "taal": "nl",
                    "content": element1.content,
                    "labels": [],
                },
                {
                    "id": str(element2.id),
                    "taal": "nl",
                    "content": element2.content,
                    "labels": [],
                },
            ],
        )

    def test_en_content_and_fallback(self):
        element1 = ContentElementFactory.create(product_type=self.product_type)
        element1.set_current_language("en")
        element1.content = "EN content"
        element1.save()

        element2 = ContentElementFactory.create(product_type=self.product_type)

        path = reverse("producttype-content", args=(self.product_type.id,))
        response = self.client.get(path, headers={"Accept-Language": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertCountEqual(
            response.data,
            [
                {
                    "id": str(element1.id),
                    "taal": "en",
                    "content": "EN content",
                    "labels": [],
                },
                {
                    "id": str(element2.id),
                    "taal": "nl",
                    "content": element2.content,
                    "labels": [],
                },
            ],
        )
