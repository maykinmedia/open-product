from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from .externeverwijzingconfig import ExterneVerwijzingConfig, VerwijzingTypes
from .producttype import ProductType


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

    zaaktypen_api = models.ForeignKey(
        ExterneVerwijzingConfig,
        limit_choices_to={"type": VerwijzingTypes.ZAAKTYPEN},
        verbose_name=_("zaaktypen api"),
        related_name="zaaktypen",
        on_delete=models.PROTECT,
        help_text=_("de api waar dit zaaktype zich bevind."),
    )

    class Meta:
        verbose_name = _("zaaktype")
        verbose_name_plural = _("zaaktypen")
        unique_together = (("producttype", "uuid"),)
        ordering = ("-id",)

    def __str__(self):
        return str(self.uuid)
