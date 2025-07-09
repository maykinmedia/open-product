from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel

from .producttype import ProductType


@reversion.register(follow=("producttype",))
class Bestand(BaseModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("producttype"),
        related_name="bestanden",
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij dit bestand hoort."),
    )
    bestand = models.FileField(verbose_name=_("bestand"))

    class Meta:
        verbose_name = _("Producttype bestand")
        verbose_name_plural = _("Producttype bestanden")
        ordering = ("-id",)

    def __str__(self):
        return f"{self.producttype.code}: {self.bestand.name}"
