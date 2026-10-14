from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel

from .producttype import ProductType


@reversion.register(follow=("producttype",))
class SubType(BaseModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("Producttype"),
        related_name="subtypen",
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij dit subtype hoort."),
    )
    naam = models.CharField(
        verbose_name=_("naam"), max_length=255, help_text=_("Naam van het subtype.")
    )

    class Meta:
        verbose_name = _("Producttype subtype")
        verbose_name_plural = _("Producttype subtype")
        ordering = ("-id",)
        unique_together = (("producttype", "naam"),)

    def save(self, *args, **kwargs):
        self.naam = self.naam.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producttype.code}: {self.naam}"
