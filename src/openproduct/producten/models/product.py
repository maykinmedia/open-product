from datetime import date
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.logging.logevent import audit_automation_update
from openproduct.producten.models.validators import validate_product_dates
from openproduct.producttypen.models import ProductType
from openproduct.producttypen.models.producttype import ProductStateChoices
from openproduct.utils.models import BasePublishableModel


class PrijsFrequentieChoices(models.TextChoices):

    EENMALIG = "eenmalig", _("Eenmalig")
    MAANDELIJKS = "maandelijks", _("Maandelijks")
    JAARLIJKS = "jaarlijks", _("Jaarlijks")


@reversion.register(follow=("eigenaren", "producttype"))
class Product(BasePublishableModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("Producttype"),
        on_delete=models.PROTECT,
        help_text=_("Het type van dit product"),
        related_name="producten",
    )
    naam = models.CharField(
        _("naam"),
        max_length=255,
        blank=True,
        help_text=_("De naam van dit product."),
    )
    start_datum = models.DateField(
        _("start datum"),
        help_text=_(
            "De start datum van dit product. Op deze datum zal de status van het product automatisch naar ACTIEF worden gezet. Op het moment dat de start_datum wordt ingevuld moet de status ACTIEF op het producttype zijn toegestaan."
        ),
        null=True,
        blank=True,
    )
    eind_datum = models.DateField(
        _("eind datum"),
        help_text=_(
            "De einddatum van dit product. Op deze datum zal de status van het product automatisch naar VERLOPEN worden gezet. Op het moment dat de eind_datum wordt ingevuld moet de status VERLOPEN op het producttype zijn toegestaan."
        ),
        null=True,
        blank=True,
    )

    status = models.CharField(
        _("status"),
        choices=ProductStateChoices.choices,
        help_text=_(
            "De status opties worden bepaald door het veld 'toegestane statussen' van het gerelateerde producttype."
        ),
        default=ProductStateChoices.INITIEEL,
    )

    prijs = models.DecimalField(
        verbose_name=_("prijs"),
        decimal_places=2,
        max_digits=8,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("De prijs van het product."),
    )

    frequentie = models.CharField(
        _("Prijs frequentie"),
        max_length=30,
        choices=PrijsFrequentieChoices.choices,
        help_text=_("De frequentie van betalingen."),
    )

    verbruiksobject = models.JSONField(
        _("verbruiksobject"),
        null=True,
        blank=True,
        help_text=_(
            "Verbruiksobject van dit product. Wordt gevalideerd met het `verbruiksobject_schema` uit het producttype."
        ),
        encoder=DjangoJSONEncoder,
    )

    dataobject = models.JSONField(
        _("dataobject"),
        null=True,
        blank=True,
        help_text=_(
            "Dataobject van dit product. Wordt gevalideerd met het `dataobject_schema` uit het producttype."
        ),
        encoder=DjangoJSONEncoder,
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Producten")

    def clean(self):
        validate_product_dates(self.start_datum, self.eind_datum)

    def save(self, *args, **kwargs):
        if self.check_start_datum():
            self.status = ProductStateChoices.ACTIEF
            super().save(*args, **kwargs)
            audit_automation_update(
                self, _("Status is naar ACTIEF gezet vanwege de start datum.")
            )

        elif self.check_eind_datum():
            self.status = ProductStateChoices.VERLOPEN
            super().save(*args, **kwargs)
            audit_automation_update(
                self, _("Status is naar VERLOPEN gezet vanwege de eind datum.")
            )

        else:
            super().save(*args, **kwargs)

    def check_start_datum(self):
        return (
            self.start_datum
            and self.start_datum <= date.today()
            and self.status
            in (ProductStateChoices.INITIEEL, ProductStateChoices.GEREED)
        )

    def check_eind_datum(self):
        return (
            self.eind_datum
            and self.eind_datum <= date.today()
            and self.status
            in (
                ProductStateChoices.INITIEEL,
                ProductStateChoices.GEREED,
                ProductStateChoices.ACTIEF,
            )
        )

    def __str__(self):
        return f"{self.producttype.naam} instantie."
