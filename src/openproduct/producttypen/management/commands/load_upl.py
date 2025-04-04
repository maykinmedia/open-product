import csv
import os
from dataclasses import dataclass
from io import StringIO

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import requests

from openproduct.producttypen.models import (
    UniformeProductNaam as UniformProductNaamModel,
)


@dataclass
class UniformProductName:
    name: str
    uri: str


def _check_if_csv_extension(path: str):
    _, extension = os.path.splitext(path)
    file_format = extension[1:]

    if file_format != "csv":
        raise CommandError("File format is not csv.")


class Command(BaseCommand):

    def __init__(self):
        self.help = (
            "Load upn to the database from a given local csv file or csv file url."
        )
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            help="The path to the csv file to be imported.",
        )
        parser.add_argument(
            "--url",
            help="The url to the csv file to be imported.",
        )

    def handle(self, **options):
        file = options.pop("file")
        url = options.pop("url")

        if file and url:
            raise CommandError("Only one of --file or --url can be specified.")

        if not file and not url:
            raise CommandError("Either --file or --url must be specified.")

        self.stdout.write(f"Importing upn from {file if file else url}...")

        try:
            if file:
                created_count, update_count, removed_count = self._parse_csv_file(file)
            else:
                created_count, update_count, removed_count = self._parse_csv_url(url)
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f"Something went wrong: {str(e)}")
        self.stdout.write(
            "Done\n"
            f"Created {created_count} product names.\n"
            f"Updated {update_count} product names.\n"
            f"{removed_count} product names did not exist in the csv."
        )

    def _parse_csv_file(self, file: str):
        _check_if_csv_extension(file)

        with open(file, encoding="utf-8-sig") as f:
            data = csv.DictReader(f)
            return self._load_upl(data)

    def _parse_csv_url(self, url: str):
        _check_if_csv_extension(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise CommandError(f"Could not connect to {url}")
        except requests.exceptions.RequestException as e:
            raise CommandError(e)

        content = StringIO(response.text)
        data = csv.DictReader(content)
        return self._load_upl(data)

    @transaction.atomic
    def _load_upl(self, data: csv.DictReader) -> tuple[int, int, int]:
        created_count = 0
        updated_count = 0
        upn_updated_list = []
        columns = {
            "uri": "URI",
            "name": "UniformeProductnaam",
        }

        if missing_columns := [
            f"'{key}'" for key in columns.values() if key not in data.fieldnames
        ]:
            raise CommandError(
                f"Column(s) {', '.join(missing_columns)} do not exist in the CSV."
            )

        for i, row in enumerate(data):
            uri = row[columns["uri"]]
            name = row[columns["name"]]

            if not name or not uri:
                self.stdout.write(
                    f"Skipping index {i} because of missing column(s) {' or '.join(columns.values())}."
                )
                continue

            upn, created = UniformProductNaamModel.objects.update_or_create(
                uri=uri,
                defaults={"naam": name, "is_verwijderd": False},
            )
            upn_updated_list.append(upn.id)

            if created:
                created_count += 1
            else:
                updated_count += 1

        removed_count = UniformProductNaamModel.objects.exclude(
            id__in=upn_updated_list
        ).update(
            is_verwijderd=True,
        )
        return created_count, updated_count, removed_count
