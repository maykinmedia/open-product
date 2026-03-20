import os
from datetime import date
from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

import requests_mock

from openproduct.locaties.models import Contact, Organisatie
from openproduct.producttypen.models import Parameter, ProductType

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestImportEvaCommand(TestCase):
    def setUp(self):
        self.path = os.path.join(TESTS_DIR, "data/upl.csv")
        self.requests_mock = requests_mock.Mocker()
        self.requests_mock.start()
        self.addCleanup(self.requests_mock.stop)

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "import_eva",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_call_command_without_file(self):
        with self.assertRaisesMessage(
            CommandError, "Error: the following arguments are required: file"
        ):
            self.call_command()

    def test_with_other_file_extension(self):
        path = os.path.join(TESTS_DIR, "data/eva.txt")
        with self.assertRaisesMessage(CommandError, "File format is not csv."):
            self.call_command(path)

    def test_import(self):
        path = os.path.join(TESTS_DIR, "data/eva.csv")
        self.call_command(path)

        producttype = ProductType.objects.get()

        self.assertEqual(producttype.naam, "AGRessie")
        self.assertEqual(producttype.code, "PCP-AGR-01")
        self.assertEqual(producttype.publicatie_start_datum, date(2020, 1, 1))
        self.assertEqual(producttype.publicatie_eind_datum, date(2382, 12, 31))

        contact = producttype.contacten.get()

        self.assertEqual(contact.naam, "L. de Haan")
        self.assertEqual(contact.organisatie.naam, "Participatie")

        self.assertCountEqual(
            producttype.parameters.values_list("naam", "waarde"),
            [
                ("Participatie monitoring", "0"),
                ("Route Inburgering", "0"),
                ("Route Participatie niet actief", "1"),
                (" Route Participatie in beweging", "0"),
                ("Route Participatie activering", "1"),
                ("Route Dhw", "0"),
                ("Route Brede intake", "0"),
                ("Route Dhw begeleiding na plaatsing", "0"),
                ("Route Sociaal intensief", "0"),
                ("Doorlooptijd in dagen", "364"),
                ("Primair (Ja/Nee)", "Y"),
            ],
        )

    def test_import_missing_columns(self):
        path = os.path.join(TESTS_DIR, "data/eva-missing-columns.csv")
        with self.assertRaisesMessage(
            CommandError, "Required column: Code contract is missing"
        ):
            self.call_command(path)

    def test_import_empty_data(self):
        path = os.path.join(TESTS_DIR, "data/eva-empty-data.csv")
        with self.assertRaisesMessage(
            CommandError, "Required field: Code contract is empty"
        ):
            self.call_command(path)

    def test_import_existing_data(self):
        path = os.path.join(TESTS_DIR, "data/eva.csv")
        self.call_command(path)
        path = os.path.join(TESTS_DIR, "data/eva.csv")
        self.call_command(path)

        self.assertEqual(ProductType.objects.count(), 1)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Organisatie.objects.count(), 1)
        self.assertEqual(Parameter.objects.count(), 11)
