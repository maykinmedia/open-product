import csv
from datetime import datetime

from django.core.management import BaseCommand, CommandError
from django.db import transaction

from openproduct.locaties.models import Contact, Organisatie

from ...models import Parameter, ProductType, Thema, UniformeProductNaam
from ...models.enums import DoelgroepChoices
from .load_upl import _check_if_csv_extension

REQUIRED_FIELDS = [
    "Code contract",
    "Naam project (naam voorziening)",
    "Datum begin contract",
    "Datum einde contract",
    "Inkoper",
    "Aanbieder",
]

MAPPING = {
    "code": "Code contract",
    "naam": "Naam project (naam voorziening)",
    "publicatie_start_datum": "Datum begin contract",
    "publicatie_eind_datum": "Datum einde contract",
}

PARAMETERS = [
    "Primair (Ja/Nee)",
    "Doorlooptijd in dagen",
    "Route Sociaal intensief",
    "Route Dhw begeleiding na plaatsing",
    "Route Brede intake",
    "Route Dhw",
    "Route Participatie activering",
    " Route Participatie in beweging",
    "Route Participatie niet actief",
    "Route Inburgering",
    "Participatie monitoring",
]

CONTACT_MAPPING = {
    "naam": "Inkoper",
    "organisatie": "Aanbieder",
}


def _check_required_fields(row: dict[str, str]):
    for field in REQUIRED_FIELDS + PARAMETERS:
        if field in row and row[field] != "":
            continue
        raise CommandError(f"Required field: {field} is empty")


def _check_required_columns(row: list[str]):
    for field in REQUIRED_FIELDS + PARAMETERS:
        if field not in row:
            raise CommandError(f"Required column: {field} is missing")


class Command(BaseCommand):
    def __init__(self):
        self.help = "Import eva data from a csv file"
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument("file")

    def handle(self, **options):
        file = options.pop("file")

        self.stdout.write(f"Importing from {file}...")

        self._parse(file)

    def _parse(self, file: str):
        _check_if_csv_extension(file)

        with open(file, encoding="utf-8-sig") as f:
            data = csv.DictReader(f, delimiter=";")
            _check_required_columns(data.fieldnames)
            return self._import_eva(data)

    @transaction.atomic
    def _import_eva(self, data: csv.DictReader):
        thema, _ = Thema.objects.get_or_create(
            naam="EVA",
        )

        upn, _ = UniformeProductNaam.objects.get_or_create(
            naam="UPL-naam nog niet beschikbaar"
        )
        try:
            for row in data:
                _check_required_fields(row)
                producttype = self._import_producttype(row, upn)
                producttype.themas.add(thema)

                contact = self._import_contact(row)
                producttype.contacten.add(contact)

                parameter_fields = {k: row[k] for k in PARAMETERS}
                self._import_parameters(producttype, parameter_fields)
        except CommandError as e:
            raise e
        except Exception as e:
            raise CommandError("Could not import", e)

    def _import_parameters(
        self, producttype: ProductType, parameter_fields: dict[str, str]
    ):
        parameters = [
            Parameter(producttype=producttype, naam=k, waarde=v)
            for k, v in parameter_fields.items()
        ]

        Parameter.objects.bulk_create(
            parameters,
            update_conflicts=True,
            unique_fields=("producttype", "naam"),
            update_fields=("waarde",),
        )

    def _import_contact(self, row: dict[str, str]) -> Contact:
        org, _ = Organisatie.objects.update_or_create(
            code=row[CONTACT_MAPPING["organisatie"]],
            defaults={"naam": row[CONTACT_MAPPING["organisatie"]]},
        )

        contact, _ = Contact.objects.update_or_create(
            naam=row[CONTACT_MAPPING["naam"]],
            organisatie=org,
        )

        return contact

    def _import_producttype(
        self, row: dict[str, str], upn: UniformeProductNaam
    ) -> ProductType:
        producttype, _ = ProductType.objects.update_or_create(
            code=row[MAPPING["code"]].replace(" ", "-"),
            defaults={
                "naam": row[MAPPING["naam"]],
                "publicatie_start_datum": datetime.strptime(
                    row[MAPPING["publicatie_start_datum"]], "%d-%m-%Y"
                ).date(),
                "publicatie_eind_datum": datetime.strptime(
                    row[MAPPING["publicatie_eind_datum"]], "%d-%m-%Y"
                ).date(),
                "doelgroep": DoelgroepChoices.BURGERS,
                "uniforme_product_naam": upn,
                "samenvatting": row[MAPPING["naam"]],
            },
        )
        return producttype
