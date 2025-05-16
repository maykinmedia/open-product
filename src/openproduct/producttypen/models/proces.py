from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .externeverwijzingconfig import ExterneVerwijzingConfig, VerwijzingTypes
from .producttype import ProductType


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

    processen_api = models.ForeignKey(
        ExterneVerwijzingConfig,
        limit_choices_to={"type": VerwijzingTypes.PROCESSEN},
        verbose_name=_("processen api"),
        related_name="processen",
        on_delete=models.PROTECT,
        help_text=_("de api waar dit proces zich bevind."),
    )

    class Meta:
        verbose_name = _("Proces")
        verbose_name_plural = _("Processen")
        unique_together = (("producttype", "uuid"),)
        ordering = ("-id",)

    def __str__(self):
        return str(self.uuid)
