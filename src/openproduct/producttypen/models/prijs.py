import datetime
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel

from .dmn_config import DmnConfig
from .producttype import ProductType


@reversion.register(follow=("producttype", "prijsopties"))
class Prijs(BaseModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="prijzen",
        help_text=_("Het producttype waarbij deze prijs hoort."),
    )
    actief_vanaf = models.DateField(
        verbose_name=_("start datum"),
        validators=[MinValueValidator(datetime.date.today)],
        help_text=_("De datum vanaf wanneer de prijs actief is."),
    )

    class Meta:
        verbose_name = _("Prijs")
        verbose_name_plural = _("Prijzen")
        unique_together = ("producttype", "actief_vanaf")

    def __str__(self):
        return f"{self.producttype.naam} {self.actief_vanaf}"


@reversion.register()
class PrijsOptie(BaseModel):
    prijs = models.ForeignKey(
        Prijs,
        verbose_name=_("prijs"),
        on_delete=models.CASCADE,
        related_name="prijsopties",
        help_text=_("De prijs waarbij deze optie hoort."),
    )
    bedrag = models.DecimalField(
        verbose_name=_("bedrag"),
        decimal_places=2,
        max_digits=8,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("Het bedrag van de prijs optie."),
    )
    beschrijving = models.CharField(
        verbose_name=_("beschrijving"),
        max_length=255,
        help_text=_("Korte beschrijving van de optie."),
    )

    class Meta:
        verbose_name = _("Prijs optie")
        verbose_name_plural = _("Prijs opties")

    def __str__(self):
        return f"{self.beschrijving} {self.bedrag}"


@reversion.register()
class PrijsRegel(BaseModel):
    beschrijving = models.CharField(
        verbose_name=_("beschrijving"),
        max_length=255,
        help_text=_("Korte beschrijving van de prijs regel."),
    )

    prijs = models.ForeignKey(
        Prijs,
        verbose_name=_("prijs"),
        on_delete=models.CASCADE,
        related_name="prijsregels",
        help_text=_("De prijs waarbij deze regel hoort."),
    )

    dmn_config = models.ForeignKey(
        DmnConfig,
        verbose_name=_("dmn config"),
        on_delete=models.CASCADE,
        related_name="prijsregels",
        help_text=_("de dmn engine waar de tabel is gedefinieerd."),
    )

    dmn_tabel_id = models.CharField(
        verbose_name=_("dmn tabel id"),
        max_length=255,
        help_text=_("id van de dmn tabel binnen de dmn instantie."),
    )

    @property
    def url(self):
        return f"{self.dmn_config.tabel_endpoint.rstrip('/')}/{self.dmn_tabel_id}"

    class Meta:
        verbose_name = _("Prijs regel")
        verbose_name_plural = _("Prijs regels")

    def __str__(self):
        return f"{self.beschrijving} {self.url}"
