from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import jsonschema
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from openproduct.utils.validators import CustomRegexValidator

from .enums import DoelgroepChoices
from .externeverwijzingconfig import ExterneVerwijzingConfig


def validate_prijs_optie_xor_regel(optie_count: int, regel_count: int):
    if optie_count and regel_count:
        raise ValidationError(_("Een prijs kan niet zowel opties als regels hebben."))

    if optie_count == 0 and regel_count == 0:
        raise ValidationError(
            _("Een prijs moet één of meerdere opties of regels hebben.")
        )


def validate_thema_gepubliceerd_state(hoofd_thema, gepubliceerd, sub_themas=None):
    if gepubliceerd and hoofd_thema and not hoofd_thema.gepubliceerd:
        raise ValidationError(
            _(
                "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
            )
        )

    if (
        not gepubliceerd
        and sub_themas
        and sub_themas.filter(gepubliceerd=True).exists()
    ):
        raise ValidationError(
            _(
                "Thema's kunnen niet ongepubliceerd worden als ze gepubliceerde sub-thema's hebben."
            )
        )


validate_producttype_code = CustomRegexValidator(
    regex="^[A-Z0-9-]+$",
    message=_("Code mag alleen hoofdletters, cijfers en koppeltekens bevatten."),
)


def check_for_circular_reference(thema, hoofd_thema):
    parent = hoofd_thema

    while parent:
        if parent is None:
            return
        if parent == thema:
            raise ValidationError(
                _("Een thema kan geen referentie naar zichzelf hebben.")
            )
        parent = parent.hoofd_thema


def check_externe_verwijzing_config_url(field_url):
    if not getattr(ExterneVerwijzingConfig.get_solo(), field_url, ""):
        raise ValidationError(
            _(
                "De {field_url} is niet geconfigureerd in de externe verwijzing config"
            ).format(field_url=field_url.replace("_", " "))
        )


def validate_dmn_mapping(mapping):
    schema = {
        "type": "object",
        "definitions": {
            "classType": {
                "type": "string",
                "enum": [
                    "String",
                    "Integer",
                    "Double",
                    "Boolean",
                    "Date",
                    "Long",
                ],
            }
        },
        "properties": {
            "static": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "classType", "value"],
                    "properties": {
                        "name": {"type": "string"},
                        "value": {"type": "string"},
                        "classType": {"$ref": "#/definitions/classType"},
                    },
                    "additionalProperties": False,
                },
            }
        },
        "additionalProperties": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "classType", "regex"],
                "properties": {
                    "name": {"type": "string"},
                    "regex": {"type": "string"},
                    "classType": {"$ref": "#/definitions/classType"},
                },
                "additionalProperties": False,
            },
        },
    }
    try:
        jsonschema.validate(mapping, schema)
    except JsonSchemaValidationError:
        raise ValidationError(
            _("De mapping komt niet overeen met het schema. (zie API spec)")
        )


def validate_publicatie_dates(publicatie_start_datum, publicatie_eind_datum):
    if publicatie_eind_datum is None:
        return

    if publicatie_start_datum is None:
        raise ValidationError(
            _(
                "De publicatie eind datum kan niet zonder een publicatie start datum worden gezet."
            )
        )

    if publicatie_start_datum >= publicatie_eind_datum:
        raise ValidationError(
            _(
                "De publicatie eind datum van een producttype mag niet op een eerdere of dezelfde dag vallen als de publicate start datum."
            )
        )


def validate_uniforme_product_naam_constraint(upl, doelgroep: DoelgroepChoices):
    if not upl and doelgroep in (
        DoelgroepChoices.BURGERS,
        DoelgroepChoices.BEDRIJVEN_EN_INSTELLINGEN,
    ):
        raise ValidationError(
            _(
                "Bij de doelgroep `Burgers` of `Bedrijven en instellingen` is een uniforme product naam verplicht."
            )
        )
