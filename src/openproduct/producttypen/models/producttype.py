from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion
from parler.fields import TranslatedField, TranslationsForeignKey
from parler.models import TranslatableModel, TranslatedFieldsModel

from openproduct.locaties.models import Contact, Locatie, Organisatie
from openproduct.utils.fields import ChoiceArrayField
from openproduct.utils.models import BasePublishableModel

from .jsonschema import JsonSchema
from .thema import Thema
from .upn import UniformeProductNaam
from .validators import validate_producttype_code, validate_publicatie_dates


class ProductStateChoices(models.TextChoices):
    INITIEEL = "initieel", _("Initieel")
    IN_AANVRAAG = "in_aanvraag", _("In aanvraag")
    GEREED = "gereed", _("Gereed")
    ACTIEF = "actief", _("Actief")
    INGETROKKEN = "ingetrokken", _("Ingetrokken")
    GEWEIGERD = "geweigerd", _("Geweigerd")
    VERLOPEN = "verlopen", _("Verlopen")


@reversion.register(
    follow=(
            "verbruiksobject_schema",
            "dataobject_schema",
            "uniforme_product_naam",
            "organisaties",
            "locaties",
            "contacten",
            "content_elementen",
            "externe_codes",
            "links",
            "parameters",
            "bestanden",
            "translations",
    )
)
class ProductType(BasePublishableModel, TranslatableModel):
    code = models.CharField(
        verbose_name=_("code"),
        max_length=255,
        help_text=_("code van het producttype."),
        unique=True,
        validators=[validate_producttype_code],
    )

    verbruiksobject_schema = models.ForeignKey(
        JsonSchema,
        verbose_name=_("verbruiksobject schema"),
        on_delete=models.PROTECT,
        help_text=_(
            "JSON schema om het verbruiksobject van een gerelateerd product te valideren."
        ),
        null=True,
        blank=True,
        related_name="producttypen_verbruiksobject_schemas",
    )

    dataobject_schema = models.ForeignKey(
        JsonSchema,
        verbose_name=_("dataobject schema"),
        on_delete=models.PROTECT,
        help_text=_(
            "JSON schema om het dataobject van een gerelateerd product te valideren."
        ),
        null=True,
        blank=True,
        related_name="producttypen_dataobject_schemas",
    )

    toegestane_statussen = ChoiceArrayField(
        models.CharField(
            choices=[
                choice
                for choice in ProductStateChoices.choices
                if choice[0] != ProductStateChoices.INITIEEL
            ]
        ),
        verbose_name=_("toegestane statussen"),
        default=list,
        blank=True,
        help_text=_("toegestane statussen voor producten van dit type."),
    )

    keywords = ArrayField(
        models.CharField(max_length=100, blank=True),
        verbose_name=_("Keywords"),
        default=list,
        blank=True,
        help_text=_("Lijst van keywords waarop kan worden gezocht."),
    )

    uniforme_product_naam = models.ForeignKey(
        UniformeProductNaam,
        verbose_name=_("Uniforme Product naam"),
        on_delete=models.CASCADE,
        help_text=_("Uniforme product naam gedefinieerd door de overheid."),
        related_name="producttypen",
    )

    themas = models.ManyToManyField(
        Thema,
        verbose_name=_("thema's"),
        blank=True,
        related_name="producttypen",
        help_text=_("thema's waaraan het producttype is gelinkt."),
    )

    organisaties = models.ManyToManyField(
        Organisatie,
        verbose_name=_("organisaties"),
        blank=True,
        related_name="producttypen",
        help_text=_("organisaties die dit het product aanbieden."),
    )

    contacten = models.ManyToManyField(
        Contact,
        verbose_name=_("contacten"),
        related_name="producttypen",
        blank=True,
        help_text=_("De contacten verantwoordelijk voor het producttype."),
    )

    locaties = models.ManyToManyField(
        Locatie,
        verbose_name=_("locaties"),
        related_name="producttypen",
        blank=True,
        help_text=_("De locaties waar het product beschikbaar is."),
    )

    interne_opmerkingen = models.TextField(
        verbose_name=_("interne opmerkingen"),
        blank=True,
        help_text=_("Interne opmerkingen over het producttype."),
    )

    publicatie_start_datum = models.DateField(
        verbose_name=_("publicatie startdatum"),
        help_text=_("De datum waarop het producttype gepubliceerd is"),
        blank=True,
        null=True,
    )

    publicatie_eind_datum = models.DateField(
        verbose_name=_("publicatie startdatum"),
        help_text=_("De datum waarop het producttype gepubliceerd is"),
        blank=True,
        null=True,
    )

    naam = TranslatedField()
    samenvatting = TranslatedField()

    class Meta:
        verbose_name = _("Producttype")
        verbose_name_plural = _("Producttypen")
        ordering = ("-id",)

    def __str__(self):
        return self.code

    def clean(self):
        validate_publicatie_dates(
            self.publicatie_start_datum, self.publicatie_eind_datum
        )

    def add_contact_organisaties(self):
        for contact in self.contacten.all():
            if (
                contact.organisatie_id is not None
                and not self.organisaties.filter(id=contact.organisatie_id).exists()
            ):
                self.organisaties.add(contact.organisatie)

    @property
    def actuele_prijs(self):
        now = date.today()
        return (
            self.prijzen.filter(actief_vanaf__lte=now).order_by("actief_vanaf").last()
        )

    @property
    def gepubliceerd(self):
        now = date.today()

        return (
            self.publicatie_start_datum is not None
            and self.publicatie_start_datum <= now
            and (not self.publicatie_eind_datum or self.publicatie_eind_datum > now)
        )


@reversion.register()
class ProductTypeTranslation(TranslatedFieldsModel):
    master = TranslationsForeignKey(
        ProductType,
        related_name="translations",
        on_delete=models.CASCADE,
        null=True,
    )
    naam = models.CharField(
        verbose_name=_("producttype naam"),
        max_length=255,
        help_text=_("naam van het producttype."),
    )

    samenvatting = models.TextField(
        verbose_name=_("samenvatting"),
        default="",
        help_text=_("Korte samenvatting van het producttype."),
    )

    class Meta:
        unique_together = ("language_code", "master")
        verbose_name = _("Producttype vertaling")
        verbose_name_plural = _("Producttype vertalingen")
        ordering = ("-id",)
