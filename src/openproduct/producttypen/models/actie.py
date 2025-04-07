from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel

from .dmn_config import DmnConfig
from .producttype import ProductType


@reversion.register(follow=("producttype",))
class Actie(BaseModel):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("naam van de actie."),
    )

    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("Producttype"),
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij deze actie hoort."),
        related_name="acties",
    )

    dmn_config = models.ForeignKey(
        DmnConfig,
        verbose_name=_("dmn config"),
        on_delete=models.PROTECT,
        related_name="acties",
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

    def __str__(self):
        return f"{self.naam} {self.url}"

    class Meta:
        verbose_name = _("actie")
        verbose_name_plural = _("acties")
        ordering = ("id",)
