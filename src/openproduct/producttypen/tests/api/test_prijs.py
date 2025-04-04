import datetime
import uuid
from decimal import Decimal

from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.producttypen.models import Prijs, PrijsOptie, PrijsRegel, ProductType
from openproduct.producttypen.tests.factories import (
    DmnConfigFactory,
    PrijsFactory,
    PrijsOptieFactory,
    PrijsRegelFactory,
    ProductTypeFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


@freeze_time("2024-01-01")
class TestProductTypePrijs(BaseApiTestCase):
    path = reverse_lazy("prijs-list")

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory()
        self.prijs_data = {
            "actief_vanaf": datetime.date(2024, 1, 2),
            "product_type_id": self.product_type.id,
        }
        self.prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 1, 2)
        )

        DmnConfigFactory.create(tabel_endpoint="https://maykinmedia.nl")

        self.path = reverse("prijs-list")
        self.detail_path = reverse("prijs-detail", args=[self.prijs.id])

    def test_read_prijs_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "actief_vanaf": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "product_type_id": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
            },
        )

    def test_create_prijs_with_empty_opties(self):
        response = self.client.post(self.path, self.prijs_data | {"prijsopties": []})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_(
                            "Een prijs moet één of meerdere opties of regels hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_prijs_with_empty_regels(self):
        response = self.client.post(self.path, self.prijs_data | {"prijsregels": []})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_(
                            "Een prijs moet één of meerdere opties of regels hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_prijs_without_opties(self):
        response = self.client.post(self.path, self.prijs_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_(
                            "Een prijs moet één of meerdere opties of regels hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_prijs_without_regels(self):
        response = self.client.post(self.path, self.prijs_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_(
                            "Een prijs moet één of meerdere opties of regels hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_prijs_with_prijs_opties(self):
        data = {
            "actief_vanaf": datetime.date(2024, 1, 3),
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
            "product_type_id": self.product_type.id,
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prijs.objects.count(), 2)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(
            PrijsOptie.objects.get().bedrag,
            Decimal("74.99"),
        )

    def test_create_prijs_with_optie_with_id(self):
        id = uuid.uuid4()
        data = {
            "actief_vanaf": datetime.date(2024, 1, 3),
            "prijsopties": [{"id": id, "bedrag": "74.99", "beschrijving": "spoed"}],
            "product_type_id": self.product_type.id,
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prijs.objects.count(), 2)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertNotEqual(PrijsOptie.objects.get().id, id)

    def test_create_prijs_with_regel_with_id(self):
        id = uuid.uuid4()
        data = {
            "actief_vanaf": datetime.date(2024, 1, 3),
            "prijsregels": [
                {
                    "id": id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "base",
                }
            ],
            "product_type_id": self.product_type.id,
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prijs.objects.count(), 2)
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertNotEqual(PrijsRegel.objects.get().id, id)

    def test_create_prijs_with_prijs_regels(self):
        data = {
            "actief_vanaf": datetime.date(2024, 1, 3),
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "spoed",
                }
            ],
            "product_type_id": self.product_type.id,
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prijs.objects.count(), 2)
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertEqual(
            response.data["prijsregels"][0]["url"],
            "https://maykinmedia.nl/iqjowijdoanwda",
        )

    def test_create_prijs_with_opties_and_regels(self):
        data = {
            "actief_vanaf": datetime.date(2024, 1, 3),
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "spoed",
                }
            ],
            "product_type_id": self.product_type.id,
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_("Een prijs kan niet zowel opties als regels hebben."),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_removing_all_opties(self):
        PrijsOptieFactory.create(prijs=self.prijs)
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_(
                            "Een prijs moet één of meerdere opties of regels hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_removing_all_regels(self):
        PrijsRegelFactory.create(prijs=self.prijs)
        PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsregels": [],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_(
                            "Een prijs moet één of meerdere opties of regels hebben."
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_removing_optie_adding_regel(self):
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "spoed",
                }
            ],
            "prijsopties": [],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["prijsregels"]), 1)
        self.assertEqual(len(response.data["prijsopties"]), 0)
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 0)

    def test_update_prijs_removing_regel_adding_optie(self):
        PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsregels": [],
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["prijsregels"]), 0)
        self.assertEqual(len(response.data["prijsopties"]), 1)
        self.assertEqual(PrijsRegel.objects.count(), 0)
        self.assertEqual(PrijsOptie.objects.count(), 1)

    def test_update_prijs_updating_and_removing_opties(self):

        optie_to_be_updated = PrijsOptieFactory.create(prijs=self.prijs)
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {
                    "id": optie_to_be_updated.id,
                    "bedrag": "20",
                    "beschrijving": optie_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.get().bedrag, Decimal("20"))
        self.assertEqual(PrijsOptie.objects.get().id, optie_to_be_updated.id)

    def test_update_prijs_updating_and_removing_regels(self):

        regel_to_be_updated = PrijsRegelFactory.create(prijs=self.prijs)
        PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsregels": [
                {
                    "id": regel_to_be_updated.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertEqual(
            response.data["prijsregels"][0]["url"],
            "https://maykinmedia.nl/iqjowijdoanwda",
        )
        self.assertEqual(PrijsRegel.objects.get().id, regel_to_be_updated.id)

    def test_update_prijs_creating_and_deleting_opties(self):

        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsopties": [{"bedrag": "20", "beschrijving": "test"}],
            "product_type_id": self.product_type.id,
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.get().bedrag, Decimal("20"))

    def test_update_prijs_creating_and_deleting_regels(self):

        PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "test",
                }
            ],
            "product_type_id": self.product_type.id,
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertEqual(
            response.data["prijsregels"][0]["url"],
            "https://maykinmedia.nl/iqjowijdoanwda",
        )

    def test_update_prijs_with_optie_not_part_of_prijs_returns_error(self):

        optie = PrijsOptieFactory.create(prijs=PrijsFactory.create())

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving}
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=_(
                            "Prijs optie id {} op index 0 is niet onderdeel van het Prijs object."
                        ).format(optie.id),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_regel_not_part_of_prijs_returns_error(self):

        regel = PrijsRegelFactory.create(prijs=PrijsFactory.create())

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsregels": [
                {
                    "id": regel.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel.beschrijving,
                }
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsregels": [
                    ErrorDetail(
                        string=_(
                            "Prijs regel id {} op index 0 is niet onderdeel van het Prijs object."
                        ).format(regel.id),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_optie_with_unknown_id_returns_error(self):

        non_existing_id = uuid.uuid4()

        data = {
            "product_type_id": self.product_type.id,
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsopties": [
                {"id": non_existing_id, "bedrag": "20", "beschrijving": "test"}
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=_("Prijs optie id {} op index 0 bestaat niet.").format(
                            non_existing_id
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_regel_with_unknown_id_returns_error(self):

        non_existing_id = uuid.uuid4()

        data = {
            "product_type_id": self.product_type.id,
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsregels": [
                {
                    "id": non_existing_id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "test",
                }
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsregels": [
                    ErrorDetail(
                        string=_("Prijs regel id {} op index 0 bestaat niet.").format(
                            non_existing_id
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_duplicate_optie_ids_returns_error(self):

        optie = PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {"id": optie.id, "bedrag": "40", "beschrijving": optie.beschrijving},
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(optie.id),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_duplicate_regel_ids_returns_error(self):

        regel = PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsregels": [
                {
                    "id": regel.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel.beschrijving,
                },
                {
                    "id": regel.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel.beschrijving,
                },
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsregels": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(regel.id),
                        code="invalid",
                    )
                ]
            },
        )

    def test_update_prijs_with_opties_and_regels(self):
        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "spoed",
                }
            ],
        }

        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_("Een prijs kan niet zowel opties als regels hebben."),
                        code="invalid",
                    )
                ]
            },
        )

    def test_partial_update_prijs(self):

        PrijsOptieFactory.create(prijs=self.prijs)

        data = {"actief_vanaf": datetime.date(2024, 1, 4)}

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.get().prijzen.get().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsOptie.objects.count(), 1)

    def test_partial_update_prijs_updating_and_removing_opties(self):

        optie_to_be_updated = PrijsOptieFactory.create(prijs=self.prijs)
        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsopties": [
                {
                    "id": optie_to_be_updated.id,
                    "bedrag": "20",
                    "beschrijving": optie_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.get().bedrag, Decimal("20"))
        self.assertEqual(PrijsOptie.objects.get().id, optie_to_be_updated.id)

    def test_partial_update_prijs_updating_and_removing_regels(self):

        regel_to_be_updated = PrijsRegelFactory.create(prijs=self.prijs)
        PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "prijsregels": [
                {
                    "id": regel_to_be_updated.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel_to_be_updated.beschrijving,
                }
            ],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertEqual(
            response.data["prijsregels"][0]["url"],
            "https://maykinmedia.nl/iqjowijdoanwda",
        )
        self.assertEqual(PrijsRegel.objects.get().id, regel_to_be_updated.id)

    def test_partial_update_prijs_creating_and_deleting_opties(self):

        PrijsOptieFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": datetime.date(2024, 1, 4),
            "prijsopties": [{"bedrag": "20", "beschrijving": "test"}],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.get().prijzen.get().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsOptie.objects.count(), 1)
        self.assertEqual(PrijsOptie.objects.get().beschrijving, "test")

    def test_partial_update_prijs_creating_and_deleting_regels(self):

        PrijsRegelFactory.create(prijs=self.prijs)

        data = {
            "actief_vanaf": datetime.date(2024, 1, 4),
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "test",
                }
            ],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Prijs.objects.count(), 1)
        self.assertEqual(
            ProductType.objects.first().prijzen.first().actief_vanaf,
            datetime.date(2024, 1, 4),
        )
        self.assertEqual(PrijsRegel.objects.count(), 1)
        self.assertEqual(PrijsRegel.objects.first().beschrijving, "test")

    def test_partial_update_with_multiple_optie_errors(self):

        optie = PrijsOptieFactory.create(prijs=self.prijs)
        optie_of_other_prijs = PrijsOptieFactory.create(prijs=PrijsFactory.create())
        non_existing_optie = uuid.uuid4()

        data = {
            "prijsopties": [
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {"id": optie.id, "bedrag": "20", "beschrijving": optie.beschrijving},
                {
                    "id": optie_of_other_prijs.id,
                    "bedrag": "30",
                    "beschrijving": optie_of_other_prijs.beschrijving,
                },
                {"id": non_existing_optie, "bedrag": "30", "beschrijving": "test"},
            ]
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsopties": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(optie.id),
                        code="invalid",
                    ),
                    ErrorDetail(
                        string=_(
                            "Prijs optie id {} op index 2 is niet onderdeel van het Prijs object."
                        ).format(optie_of_other_prijs.id),
                        code="invalid",
                    ),
                    ErrorDetail(
                        string=_("Prijs optie id {} op index 3 bestaat niet.").format(
                            non_existing_optie
                        ),
                        code="invalid",
                    ),
                ]
            },
        )

    def test_partial_update_with_multiple_regel_errors(self):

        regel = PrijsRegelFactory.create(prijs=self.prijs)
        regel_of_other_prijs = PrijsRegelFactory.create(prijs=PrijsFactory.create())
        non_existing_regel = uuid.uuid4()

        data = {
            "prijsregels": [
                {
                    "id": regel.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel.beschrijving,
                },
                {
                    "id": regel.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel.beschrijving,
                },
                {
                    "id": regel_of_other_prijs.id,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": regel_of_other_prijs.beschrijving,
                },
                {
                    "id": non_existing_regel,
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "test",
                },
            ]
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "prijsregels": [
                    ErrorDetail(
                        string=_("Dubbel id: {} op index 1.").format(regel.id),
                        code="invalid",
                    ),
                    ErrorDetail(
                        string=_(
                            "Prijs regel id {} op index 2 is niet onderdeel van het Prijs object."
                        ).format(regel_of_other_prijs.id),
                        code="invalid",
                    ),
                    ErrorDetail(
                        string=_("Prijs regel id {} op index 3 bestaat niet.").format(
                            non_existing_regel
                        ),
                        code="invalid",
                    ),
                ]
            },
        )

    def test_partial_update_prijs_with_opties_and_regels(self):
        data = {
            "actief_vanaf": self.prijs.actief_vanaf,
            "product_type_id": self.product_type.id,
            "prijsopties": [{"bedrag": "74.99", "beschrijving": "spoed"}],
            "prijsregels": [
                {
                    "tabel_endpoint": "https://maykinmedia.nl",
                    "dmn_tabel_id": "iqjowijdoanwda",
                    "beschrijving": "spoed",
                }
            ],
        }

        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "opties_or_regels": [
                    ErrorDetail(
                        string=_("Een prijs kan niet zowel opties als regels hebben."),
                        code="invalid",
                    )
                ]
            },
        )

    def test_read_prijzen(self):
        prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=datetime.date(2024, 2, 2)
        )
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.prijs.id),
                "actief_vanaf": str(self.prijs.actief_vanaf),
                "prijsopties": [],
                "prijsregels": [],
                "product_type_id": self.product_type.id,
            },
            {
                "id": str(prijs.id),
                "actief_vanaf": str(prijs.actief_vanaf),
                "prijsopties": [],
                "prijsregels": [],
                "product_type_id": self.product_type.id,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_prijs(self):
        response = self.client.get(self.detail_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(self.prijs.id),
            "actief_vanaf": str(self.prijs.actief_vanaf),
            "prijsopties": [],
            "prijsregels": [],
            "product_type_id": self.product_type.id,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_prijs(self):

        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Prijs.objects.count(), 0)
        self.assertEqual(PrijsOptie.objects.count(), 0)
