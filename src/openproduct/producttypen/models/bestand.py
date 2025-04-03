from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .producttype import ProductType


class Bestand(BaseModel):
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("product type"),
        related_name="bestanden",
        on_delete=models.CASCADE,
        help_text=_("Het product type waarbij dit bestand hoort."),
    )
    bestand = models.FileField(verbose_name=_("bestand"))

    class Meta:
        verbose_name = _("Product type bestand")
        verbose_name_plural = _("Product type bestanden")

    def __str__(self):
        return f"{self.product_type}: {self.bestand.name}"
