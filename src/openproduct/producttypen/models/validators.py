from django.conf import settings
from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

import jsonschema
from jsonschema._format import draft202012_format_checker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from openproduct.utils.validators import CustomRegexValidator

from .dmn_config import DmnConfig
from .enums import ActieTypeChoices, DoelgroepChoices
from openproduct.producttypen.schemas import API_SCHEMA, DMN_SCHEMA, FORM_SCHEMA


def check_meervoudig_facettype(facet_type):
    """
    Prevent disabling ``meervoudig_toegestaan`` while product
    types still have multiple values of this facettype.
    """

    from openproduct.producttypen.models import ProductType

    if not facet_type.pk or facet_type.meervoudig_toegestaan:
        return

    if (
        ProductType.objects.filter(facetten__facet_type=facet_type)
        .annotate(total=Count("facetten"))
        .filter(total__gt=1)
        .exists()
    ):
        raise ValidationError(
            {
                "meervoudig_toegestaan": _(
                    "Kan niet uitgezet worden: er zijn producttypen met meerdere waarden van dit facet."
                )
            }
        )


def validate_verplichte_facetten(facet_waarden):
    """
    Ensure all mandatory (``verplicht``) facettypes are present in ``facet_waarden``.
    """

    from openproduct.producttypen.models import FacetType

    facet_types_ids = {waarde.facet_type_id for waarde in facet_waarden}
    missing = FacetType.objects.filter(verplicht=True).exclude(pk__in=facet_types_ids)
    if missing.exists():
        raise ValidationError(
            _("Verplichte facettypes ontbreken: %(namen)s.")
            % {"namen": ", ".join(missing.values_list("naam", flat=True))}
        )


def validate_meervoudig_facetten(facet_waarden):
    """
    Ensure single-value facettypes have at most one value in ``facet_waarden``.
    """

    dict_type = defaultdict(list)
    for waarde in facet_waarden:
        dict_type[waarde.facet_type].append(waarde)

    errors = [
        ValidationError(
            _("Facettype '%(type)s' staat maar één waarde toe, gekregen: %(waarden)s."),
            params={
                "type": facet_type.naam,
                "waarden": ", ".join(w.naam for w in waarden),
            },
        )
        for facet_type, waarden in dict_type.items()
        if not facet_type.meervoudig_toegestaan and len(waarden) > 1
    ]
    if errors:
        raise ValidationError(errors)


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


def validate_dmn_mapping(mapping):
    "model dmn schema validator"
    try:
        validate_schema(mapping, DMN_SCHEMA)
    except ValidationError as exc:
        raise ValidationError(exc.messages)


def validate_schema(mapping, schema):
    try:
        jsonschema.validate(
            mapping,
            schema,
            format_checker=draft202012_format_checker
            if settings.JSONSCHEMA_USE_FORMAT_CHECKER
            else None,
        )
    except JsonSchemaValidationError:
        raise ValidationError(
            {
                "mapping": _(
                    "De mapping komt niet overeen met het schema. (zie API spec)"
                )
            }
        )


def validate_publicatie_dates(publicatie_start_datum, publicatie_eind_datum):
    if publicatie_eind_datum is None:
        return

    if publicatie_start_datum is None:
        raise ValidationError(
            {
                "publicatie_eind_datum": _(
                    "De publicatie eind datum kan niet zonder een publicatie start datum worden gezet."
                )
            }
        )

    if publicatie_start_datum >= publicatie_eind_datum:
        raise ValidationError(
            {
                "publicatie_eind_datum": _(
                    "De publicatie eind datum van een producttype mag niet op een eerdere of dezelfde dag vallen als de publicate start datum."
                )
            }
        )


def validate_uniforme_product_naam_constraint(upl, doelgroep: DoelgroepChoices):
    if not upl and doelgroep in (
        DoelgroepChoices.BURGERS,
        DoelgroepChoices.BEDRIJVEN_EN_INSTELLINGEN,
    ):
        raise ValidationError(
            {
                "doelgroep": _(
                    "Bij de doelgroep `Burgers` of `Bedrijven en instellingen` is een uniforme product naam verplicht."
                )
            }
        )


def validate_exactly_one_producttype_or_thema(*, producttype, thema):
    """
    Ensure exactly ONE of (producttype, thema) is provided.
    """
    if producttype and thema:
        raise ValidationError(_("Kies óf een producttype of een thema, niet beide."))

    if not producttype and not thema:
        raise ValidationError(_("Geef een producttype of thema op."))


def validate_actie_mapping(mapping: dict | None, type: str):
    """mapping is validated by schema based on actie type"""
    if not mapping:
        return
    match type:
        case ActieTypeChoices.API:
            validate_schema(mapping, API_SCHEMA)
        case ActieTypeChoices.DMN:
            validate_schema(mapping, DMN_SCHEMA)
        case ActieTypeChoices.FORMULIER:
            validate_schema(mapping, FORM_SCHEMA)


def validate_actie_method(method: str, type: str):
    """method is required when type is API. Otherwise the field should be empty."""
    if (type == ActieTypeChoices.API) != bool(method):
        raise ValidationError(
            {
                "method": _(
                    "Method is alleen toegestaan (en verplicht) bij een 'api' actie"
                )
            }
        )


def validate_actie_dmn(dmn_config: DmnConfig, dmn_tabel_id: str, type: str):
    """dmn fields are required when type is DMN. Otherwise the fields should be empty."""
    if (type == ActieTypeChoices.DMN) != bool(dmn_config and dmn_tabel_id):
        raise ValidationError(
            {
                "dmn_config": _(
                    "Dmn velden zijn alleen toegestaan (en verplicht) bij een 'dmn' actie"
                )
            }
        )


def validate_actie_direct_url(url: str, type: str):
    """direct url is required when type is API or FORMULIER. Otherwise the field should be empty."""
    if (type in (ActieTypeChoices.API, ActieTypeChoices.FORMULIER)) != bool(url):
        raise ValidationError(
            {
                "direct_url": _(
                    "Direct url is alleen toegestaan (en verplicht) bij een 'api' of `formulier` actie"
                )
            }
        )
