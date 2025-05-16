from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .externeverwijzingconfig import ExterneVerwijzingConfig, VerwijzingTypes
from .producttype import ProductType


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

    verzoektypen_api = models.ForeignKey(
        ExterneVerwijzingConfig,
        limit_choices_to={"type": VerwijzingTypes.VERZOEKTYPEN},
        verbose_name=_("verzoekttypen api"),
        related_name="verzoekttypen",
        on_delete=models.PROTECT,
        help_text=_("de api waar dit verzoekttype zich bevind."),
    )

    class Meta:
        verbose_name = _("verzoektype")
        verbose_name_plural = _("verzoektypen")
        unique_together = (("producttype", "uuid"),)
        ordering = ("-id",)

    def __str__(self):
        return str(self.uuid)
