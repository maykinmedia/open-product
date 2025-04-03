import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from openproduct.producttypen.models.producttype import ProductStateChoices


def validate_bsn(bsn: str):
    """
    Validates that a bsn number is 9 digits and runs the 11 check.
    """

    if not re.match(r"^[0-9]{9}$", bsn):
        raise ValidationError(_("Een bsn nummer bestaat uit 9 cijfers."))

    total = sum(int(num) * (9 - i) for i, num in enumerate(bsn[:8]))
    total += int(bsn[8]) * -1

    if total == 0 or total % 11 != 0:
        raise ValidationError(_("Ongeldig bsn number."))


def validate_eigenaar_identifier(bsn, kvk_nummer, klantnummer):

    if (not (bsn or klantnummer) and not kvk_nummer) or (
        (bsn or klantnummer) and kvk_nummer
    ):
        raise ValidationError(
            _(
                "Een eigenaar moet een bsn (en/of klantnummer) of een kvk nummer (met of zonder vestigingsnummer) hebben."
            )
        )


def validate_eigenaar_vestingsnummer_only_with_kvk(kvk_nummer, vestigingsnummer):
    if vestigingsnummer and not kvk_nummer:
        raise ValidationError(
            {
                "vestigingsnummer": _(
                    "Een vestigingsnummer kan alleen in combinatie met een kvk nummer worden ingevuld."
                )
            }
        )


def validate_product_status(status, product_type):
    if (
        status != ProductStateChoices.INITIEEL
        and status not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "status": _(
                    "Status '{}' is niet toegestaan voor het product type {}."
                ).format(
                    ProductStateChoices(status).label,
                    product_type.naam,
                )
            }
        )


def validate_product_dates(start_datum, eind_datum):
    if start_datum and eind_datum and (start_datum >= eind_datum):
        raise ValidationError(
            _(
                "De eind datum van een product mag niet op een eerdere of dezelfde dag vallen als de start datum."
            )
        )


def validate_product_start_datum(start_datum, product_type):

    if (
        start_datum
        and ProductStateChoices.ACTIEF not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "start_datum": _(
                    "De start datum van het product kan niet worden gezet omdat de status ACTIEF niet is toegestaan op het product type."
                )
            }
        )


def validate_product_eind_datum(eind_datum, product_type):
    if (
        eind_datum
        and ProductStateChoices.VERLOPEN not in product_type.toegestane_statussen
    ):
        raise ValidationError(
            {
                "eind_datum": _(
                    "De eind datum van het product kan niet worden gezet omdat de status VERLOPEN niet is toegestaan op het product type."
                )
            }
        )


def validate_product_verbruiksobject(verbruiksobject, product_type):
    try:
        if (
            verbruiksobject is not None
            and product_type.verbruiksobject_schema is not None
        ):
            product_type.verbruiksobject_schema.validate(verbruiksobject)
    except ValidationError:
        raise ValidationError(
            {
                "verbruiksobject": _(
                    "Het verbruiksobject komt niet overeen met het schema gedefinieerd op het product type."
                )
            },
        )


def validate_product_dataobject(dataobject, product_type):
    try:
        if dataobject is not None and product_type.dataobject_schema is not None:
            product_type.dataobject_schema.validate(dataobject)
    except ValidationError:
        raise ValidationError(
            {
                "dataobject": _(
                    "Het dataobject komt niet overeen met het schema gedefinieerd op het product type."
                )
            },
        )
