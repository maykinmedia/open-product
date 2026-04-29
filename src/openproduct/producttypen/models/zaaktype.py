from django.db import models
from django.utils.translation import gettext_lazy as _

from ...urn.models import UrnAbstractModel
from .producttype import ProductType


class ZaakType(UrnAbstractModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("producttype"),
        related_name="zaaktypen",
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij dit zaaktype hoort."),
    )

    class Meta:
        verbose_name = _("zaaktype")
        verbose_name_plural = _("zaaktypen")
        ordering = ("-id",)
        unique_together = (("producttype", "urn"), ("producttype", "url"))

    def __str__(self):
        if self.urn:
            return self.urn
        elif self.url:
            return self.url
        return f"zaaktype {self.pk}"
