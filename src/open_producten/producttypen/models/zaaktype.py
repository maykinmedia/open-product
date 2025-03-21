from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.producttypen.models import ProductType
from open_producten.utils.models import BaseModel


class ZaakType(BaseModel):

    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        null=True,
        blank=True,
        help_text=_("Uuid van het zaaktype."),
    )

    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("product type"),
        related_name="zaaktypen",
        on_delete=models.CASCADE,
        help_text=_("Het product type waarbij dit zaaktype hoort."),
    )

    class Meta:
        verbose_name = _("zaaktype")
        verbose_name_plural = _("zaaktypen")
        unique_together = (("product_type", "uuid"),)

    def __str__(self):
        return str(self.uuid)
