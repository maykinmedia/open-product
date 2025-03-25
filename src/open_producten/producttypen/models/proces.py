from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from open_producten.utils.models import BaseModel

from .externeverwijzingconfig import ExterneVerwijzingConfig
from .producttype import ProductType


class Proces(BaseModel):

    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        null=True,
        blank=True,
        help_text=_("Uuid van het proces."),
    )

    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("product type"),
        related_name="processen",
        on_delete=models.CASCADE,
        help_text=_("Het product type waarbij dit proces hoort."),
    )

    class Meta:
        verbose_name = _("Proces")
        verbose_name_plural = _("Processen")
        unique_together = (("product_type", "uuid"),)

    def clean(self):
        check_processen_url()

    def __str__(self):
        return str(self.uuid)


def check_processen_url():
    if not ExterneVerwijzingConfig.get_solo().processen_url:
        raise ValidationError(
            _("De processen url is niet geconfigureerd in de externe verwijzing config")
        )
