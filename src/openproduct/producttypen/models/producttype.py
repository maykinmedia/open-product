from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from openproduct.locaties.models import Contact, Locatie, Organisatie
from openproduct.utils.fields import ChoiceArrayField
from openproduct.utils.models import BasePublishableModel

from .jsonschema import JsonSchema
from .thema import Thema
from .upn import UniformeProductNaam


class ProductStateChoices(models.TextChoices):

    INITIEEL = "initieel", _("Initieel")
    GEREED = "gereed", _("Gereed")
    ACTIEF = "actief", _("Actief")
    INGETROKKEN = "ingetrokken", _("Ingetrokken")
    GEWEIGERD = "geweigerd", _("Geweigerd")
    VERLOPEN = "verlopen", _("Verlopen")


class ProductType(BasePublishableModel, TranslatableModel):

    code = models.CharField(
        verbose_name=_("code"),
        max_length=255,
        help_text=_("code van het product type."),
        unique=True,
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
        related_name="product_typen_verbruiksobject_schemas",
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
        related_name="product_typen_dataobject_schemas",
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
        related_name="product_typen",
    )

    themas = models.ManyToManyField(
        Thema,
        verbose_name=_("thema's"),
        blank=True,
        related_name="product_typen",
        help_text=_("thema's waaraan het product type is gelinkt."),
    )

    organisaties = models.ManyToManyField(
        Organisatie,
        verbose_name=_("organisaties"),
        blank=True,
        related_name="product_typen",
        help_text=_("organisaties die dit het product aanbieden."),
    )

    contacten = models.ManyToManyField(
        Contact,
        verbose_name=_("contacten"),
        related_name="product_typen",
        blank=True,
        help_text=_("De contacten verantwoordelijk voor het product type."),
    )

    locaties = models.ManyToManyField(
        Locatie,
        verbose_name=_("locaties"),
        related_name="product_typen",
        blank=True,
        help_text=_("De locaties waar het product beschikbaar is."),
    )

    interne_opmerkingen = models.TextField(
        verbose_name=_("interne opmerkingen"),
        blank=True,
        help_text=_("Interne opmerkingen over het product type."),
    )

    translations = TranslatedFields(
        samenvatting=models.TextField(
            verbose_name=_("samenvatting"),
            default="",
            help_text=_("Korte samenvatting van het product type."),
        ),
        naam=models.CharField(
            verbose_name=_("product type naam"),
            max_length=255,
            help_text=_("naam van het product type."),
        ),
    )

    class Meta:
        verbose_name = _("Product type")
        verbose_name_plural = _("Product typen")

    def __str__(self):
        return self.naam

    def clean(self, *args, **kwargs):
        self.add_contact_organisaties()

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
