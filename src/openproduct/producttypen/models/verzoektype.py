from django.db import models
from django.utils.translation import gettext_lazy as _

from ...urn.models import UrnAbstractModel
from .producttype import ProductType


class VerzoekType(UrnAbstractModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("producttype"),
        related_name="verzoektypen",
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij dit verzoektype hoort."),
    )

    class Meta:
        verbose_name = _("verzoektype")
        verbose_name_plural = _("verzoektypen")
        ordering = ("-id",)
        unique_together = (("producttype", "urn"), ("producttype", "url"))

    def __str__(self):
        return self.urn if self.urn else self.url
