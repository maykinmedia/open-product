from django.db import models
from django.utils.translation import gettext_lazy as _

from ...urn.models import UrnAbstractModel
from .producttype import ProductType


class Proces(UrnAbstractModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("producttype"),
        related_name="processen",
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij dit proces hoort."),
    )

    class Meta:
        verbose_name = _("Proces")
        verbose_name_plural = _("Processen")
        ordering = ("-id",)
        unique_together = (("producttype", "urn"), ("producttype", "url"))

    def __str__(self):
        return self.urn if self.urn else self.url
