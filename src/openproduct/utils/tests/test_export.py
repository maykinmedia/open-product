import io
import zipfile
from io import StringIO
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.http import HttpResponse
from django.test import TestCase

from openproduct.locaties.tests.factories import (
    ContactFactory,
    LocatieFactory,
    OrganisatieFactory,
)
from openproduct.producttypen.tests.factories import (
    LinkFactory,
    ParameterFactory,
    PrijsFactory,
    PrijsOptieFactory,
    ProductTypeFactory,
    UniformeProductNaamFactory,
)


# @patch('openproduct.utils.management.commands.export.Command._create_zip', new=Mock())
class TestExport(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "export",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def setUp(self):
        self.upn = UniformeProductNaamFactory.create()

        self.locatie1 = LocatieFactory.create()
        self.locatie2 = LocatieFactory.create()

        self.organisatie1 = OrganisatieFactory.create()
        self.organisatie2 = OrganisatieFactory.create()

        self.contact1 = ContactFactory.create()
        self.contact2 = ContactFactory.create(organisatie=self.organisatie2)

        self.producttype1 = ProductTypeFactory.create(uniforme_product_naam=self.upn)
        self.producttype1.locaties.add(self.locatie1)
        self.producttype1.organisaties.add(self.organisatie1)
        self.producttype1.contacten.add(self.contact1)

        self.producttype1.locaties.add(self.locatie2)
        self.producttype1.organisaties.add(self.organisatie2)
        self.producttype1.contacten.add(self.contact2)

        self.producttype2 = ProductTypeFactory.create(uniforme_product_naam=self.upn)
        self.producttype2.locaties.add(self.locatie2)
        self.producttype2.organisaties.add(self.organisatie2)
        self.producttype2.contacten.add(self.contact2)

        self.link1 = LinkFactory.create(producttype=self.producttype1)
        self.link2 = LinkFactory.create(producttype=self.producttype2)

        self.prijs1 = PrijsFactory.create(producttype=self.producttype1)
        self.prijs2 = PrijsFactory.create(producttype=self.producttype2)

        self.optie1 = PrijsOptieFactory.create(prijs=self.prijs1)
        self.optie2 = PrijsOptieFactory.create(prijs=self.prijs2)

        self.param1 = ParameterFactory.create(producttype=self.producttype1)
        self.param2 = ParameterFactory.create(producttype=self.producttype2)

    def test_arguments(self):
        with self.subTest("app & model"):
            with self.assertRaisesMessage(
                CommandError, "Error: the following arguments are required: app, model"
            ):
                self.call_command()

        with self.subTest("archive_name and response"):
            with self.assertRaisesMessage(
                CommandError,
                "Please use either the --archive_name or --response argument",
            ):
                self.call_command(
                    "producttypen",
                    "producttype",
                    archive_name="test.zip",
                    response=HttpResponse(),
                )

        with self.subTest("no archive_name and response"):
            with self.assertRaisesMessage(
                CommandError,
                "Please use either the --archive_name or --response argument",
            ):
                self.call_command(
                    "producttypen",
                    "producttype",
                )

        with self.subTest("non existing model"):
            with self.assertRaisesMessage(
                CommandError,
                "Could not find model producttypen abc",
            ):
                self.call_command(
                    "producttypen",
                    "abc",
                    archive_name="test.zip",
                )

    @patch("openproduct.utils.management.commands.export.Command._create_zip")
    def test_create_with_specified_id(self, mock_create_zip):
        self.maxDiff = None

        self.call_command(
            "producttypen",
            "producttype",
            ids=[self.producttype1.id],
            archive_name="test.zip",
        )
        expected = {
            "contact": [
                {
                    "id": self.contact1.id,
                    "organisatie_id": self.contact1.organisatie.id,
                },
                {
                    "id": self.contact2.id,
                    "organisatie_id": self.contact2.organisatie.id,
                },
            ],
            "link": [
                {
                    "id": self.link1.id,
                    "producttype_id": self.producttype1.id,
                }
            ],
            "locatie": [
                {
                    "id": self.locatie1.id,
                },
                {
                    "id": self.locatie2.id,
                },
            ],
            "organisatie": [
                {
                    "id": self.organisatie1.id,
                },
                {
                    "id": self.organisatie2.id,
                },
                {
                    "id": self.contact1.organisatie.id,
                },
            ],
            "parameter": [
                {
                    "id": self.param1.id,
                    "producttype_id": self.producttype1.id,
                }
            ],
            "prijs": [
                {
                    "id": self.prijs1.id,
                    "producttype_id": self.producttype1.id,
                }
            ],
            "prijsoptie": [
                {
                    "id": self.optie1.id,
                    "prijs_id": self.prijs1.id,
                }
            ],
            "producttype": [
                {
                    "contacten_ids": [self.contact1.id, self.contact2.id],
                    "dataobject_schema_id": None,
                    "verbruiksobject_schema_id": None,
                    "id": self.producttype1.id,
                    "locaties_ids": [self.locatie1.id, self.locatie2.id],
                    "organisaties_ids": [self.organisatie1.id, self.organisatie2.id],
                    "themas_ids": [],
                    "uniforme_product_naam_id": self.upn.id,
                }
            ],
            "producttypetranslation": [
                {
                    "id": self.producttype1.translations.get().id,
                    "master_id": self.producttype1.id,
                }
            ],
            "uniformeproductnaam": [
                {
                    "id": self.upn.id,
                }
            ],
        }

        result = mock_create_zip.call_args.args[1]

        # ignore non id values and sort lists
        result = {
            key: [
                {
                    k: sorted(v) if isinstance(v, list) else v
                    for k, v in item.items()
                    if "_id" in k or k == "id"
                }
                for item in lst
            ]
            for key, lst in result.items()
        }

        for k in expected:
            self.assertCountEqual(expected[k], result[k])

    @patch("openproduct.utils.management.commands.export.Command._create_zip")
    def test_create_csv(self, mock_create_zip):
        self.call_command(
            "producttypen",
            "producttype",
            ids=[self.producttype1.id],
            archive_name="test.zip",
            format="csv",
        )

        result = mock_create_zip.call_args.args[1]

        # m2m are separate csv's
        self.assertIn("producttypen_locaties", result)
        self.assertIn("producttypen_contacten", result)
        self.assertIn("producttypen_organisaties", result)
        self.assertIn("producttypen_themas", result)

    @patch("openproduct.utils.management.commands.export.Command._create_zip")
    def test_exclude(self, mock_create_zip):
        self.call_command(
            "producttypen",
            "producttype",
            ids=[self.producttype1.id],
            archive_name="test.zip",
            exclude=["locaties"],
        )

        result = mock_create_zip.call_args.args[1]

        self.assertNotIn("producttypen_locaties", result)
        self.assertNotIn("locatie", result)
        self.assertNotIn("locaties_ids", result["producttype"][0])

    @patch("openproduct.utils.management.commands.export.Command._create_zip")
    def test_no_duplicates(self, mock_create_zip):
        self.call_command(
            "producttypen",
            "producttype",
            archive_name="test.zip",
        )

        result = mock_create_zip.call_args.args[1]

        producttype_by_id = {p["id"]: p for p in result["producttype"]}

        pt_1 = producttype_by_id.get(self.producttype1.id)
        pt_2 = producttype_by_id.get(self.producttype2.id)

        self.assertCountEqual(
            pt_1["locaties_ids"], [self.locatie1.id, self.locatie2.id]
        )
        self.assertEqual(pt_2["locaties_ids"], [self.locatie2.id])

        locaties = [loc["id"] for loc in result["locatie"]]

        self.assertCountEqual(locaties, [self.locatie1.id, self.locatie2.id])

    def test_response(self):
        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment;filename={}".format("test.zip")

        self.call_command(
            "producttypen",
            "producttype",
            ids=[self.producttype1.id],
            response=response,
        )

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
            self.assertCountEqual(
                zip.namelist(),
                [
                    "producttype.json",
                    "uniformeproductnaam.json",
                    "organisatie.json",
                    "contact.json",
                    "locatie.json",
                    "producttypetranslation.json",
                    "link.json",
                    "parameter.json",
                    "prijs.json",
                    "prijsoptie.json",
                ],
            )
