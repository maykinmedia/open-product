from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .producttype import ProductType
from .validators import check_externe_verwijzing_config_url


class ZaakType(BaseModel):
    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        help_text=_("Uuid van het zaaktype."),
    )

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
        unique_together = (("producttype", "uuid"),)
        ordering = ("-id",)

    def clean(self):
        check_externe_verwijzing_config_url("zaaktypen_url")

    def __str__(self):
        return str(self.uuid)
