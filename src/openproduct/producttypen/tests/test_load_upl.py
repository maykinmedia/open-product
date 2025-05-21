import os
from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

import requests_mock
from requests.exceptions import ConnectionError

from openproduct.producttypen.models import UniformeProductNaam
from openproduct.producttypen.tests.factories import UniformeProductNaamFactory

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestLoadUPLCommand(TestCase):
    def setUp(self):
        self.path = os.path.join(TESTS_DIR, "data/upl.csv")
        self.requests_mock = requests_mock.Mocker()
        self.requests_mock.start()
        self.addCleanup(self.requests_mock.stop)

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "load_upl",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_call_command_without_file_and_url(self):
        with self.assertRaisesMessage(
            CommandError, "Either --file or --url must be specified."
        ):
            self.call_command()

    def test_call_command_wit_file_and_url(self):
        with self.assertRaisesMessage(
            CommandError, "Only one of --file or --url can be specified."
        ):
            self.call_command("--file", self.path, "--url", "https://example.com")

    def test_with_other_file_extension(self):
        path = os.path.join(TESTS_DIR, "data/upl.txt")
        with self.assertRaisesMessage(CommandError, "File format is not csv."):
            self.call_command("--file", path)

    def test_with_csv_file(self):
        result = self.call_command("--file", self.path)
        self.assertEqual(
            result,
            f"Importing upn from {self.path}...\nDone\nCreated 1 product names.\nUpdated 0 product names.\n0 product names did not exist in the csv.\n",
        )

        self.assertEqual(UniformeProductNaam.objects.count(), 1)
        self.assertEqual(
            UniformeProductNaam.objects.get().naam, "aangifte vertrek buitenland"
        )
        self.assertEqual(
            UniformeProductNaam.objects.get().uri,
            "http://standaarden.overheid.nl/owms/terms/AangifteVertrekBuitenland",
        )

    def test_with_csv_url_404(self):
        self.requests_mock.get(
            status_code=404,
            url="https://test/upl.csv",
        )

        with self.assertRaisesMessage(
            CommandError, "404 Client Error: None for url: https://test/upl.csv"
        ):
            self.call_command("--url", "https://test/upl.csv")

    def test_wih_csv_url_connection_error(self):
        self.requests_mock.get(exc=ConnectionError, url="https://test/upl.csv")

        with self.assertRaisesMessage(
            CommandError, "Could not connect to https://test/upl.csv"
        ):
            self.call_command("--url", "https://test/upl.csv")

    def test_parse_csv_url(self):
        with open(self.path) as f:
            self.requests_mock.get(
                status_code=200,
                text=f.read(),
                url="https://test/upl.csv",
            )

            result = self.call_command("--url", "https://test/upl.csv")

        self.assertEqual(
            result,
            "Importing upn from https://test/upl.csv...\nDone\nCreated 1 product names.\nUpdated 0 product names.\n0 product names did not exist in the csv.\n",
        )

        self.assertEqual(UniformeProductNaam.objects.count(), 1)
        self.assertEqual(
            UniformeProductNaam.objects.get().naam, "aangifte vertrek buitenland"
        )
        self.assertEqual(
            UniformeProductNaam.objects.get().uri,
            "http://standaarden.overheid.nl/owms/terms/AangifteVertrekBuitenland",
        )

    def test_load_upl_with_empty_data_at_column(self):
        path = os.path.join(TESTS_DIR, "data/upl-empty-data.csv")

        result = self.call_command("--file", path)
        self.assertEqual(
            result,
            f"Importing upn from {path}...\nSkipping index 0 because of missing column(s) URI or UniformeProductnaam.\nDone\nCreated 0 product names.\nUpdated 0 product names.\n0 product names did not exist in the csv.\n",
        )

        self.assertEqual(UniformeProductNaam.objects.count(), 0)

    def test_load_csv_with_missing_columns(self):
        path = os.path.join(TESTS_DIR, "data/upl-missing-columns.csv")

        with self.assertRaisesMessage(
            CommandError, "Column(s) 'URI' do not exist in the CSV."
        ):
            self.call_command("--file", path)

    def test_upn_is_updated(self):
        UniformeProductNaamFactory.create(
            uri="http://standaarden.overheid.nl/owms/terms/AangifteVertrekBuitenland"
        )

        result = self.call_command("--file", self.path)
        self.assertEqual(
            result,
            f"Importing upn from {self.path}...\nDone\nCreated 0 product names.\nUpdated 1 product names.\n0 product names did not exist in the csv.\n",
        )

        self.assertEqual(UniformeProductNaam.objects.count(), 1)
        self.assertEqual(
            UniformeProductNaam.objects.get().naam, "aangifte vertrek buitenland"
        )
        self.assertEqual(
            UniformeProductNaam.objects.get().uri,
            "http://standaarden.overheid.nl/owms/terms/AangifteVertrekBuitenland",
        )

    def test_upn_not_in_csv_is_set_to_deleted(self):
        upn = UniformeProductNaamFactory.create(
            uri="http://standaarden.overheid.nl/owms/terms/BlaBla"
        )

        result = self.call_command("--file", self.path)
        self.assertEqual(
            result,
            f"Importing upn from {self.path}...\nDone\nCreated 1 product names.\nUpdated 0 product names.\n1 product names did not exist in the csv.\n",
        )

        self.assertEqual(UniformeProductNaam.objects.count(), 2)
        self.assertEqual(
            UniformeProductNaam.objects.filter(is_verwijderd=True).get().naam, upn.naam
        )
