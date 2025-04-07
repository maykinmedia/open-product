from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .producttype import ProductType
from .validators import check_externe_verwijzing_config_url


class VerzoekType(BaseModel):

    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        help_text=_("Uuid van het verzoektype."),
    )

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
        unique_together = (("producttype", "uuid"),)

    def clean(self):
        check_externe_verwijzing_config_url("verzoektypen_url")

    def __str__(self):
        return str(self.uuid)
