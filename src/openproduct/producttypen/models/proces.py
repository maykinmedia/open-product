from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .producttype import ProductType
from .validators import check_externe_verwijzing_config_url


class Proces(BaseModel):

    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        help_text=_("Uuid van het proces."),
    )

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
        unique_together = (("producttype", "uuid"),)

    def clean(self):
        check_externe_verwijzing_config_url("processen_url")

    def __str__(self):
        return str(self.uuid)
