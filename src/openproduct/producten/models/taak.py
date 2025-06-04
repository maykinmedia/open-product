from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.producttypen.models.validators import (
    check_externe_verwijzing_config_url,
)
from openproduct.utils.models import BaseModel

from .product import Product


class Taak(BaseModel):
    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        help_text=_("Uuid van de taak."),
    )

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="taken",
        on_delete=models.CASCADE,
        help_text=_("Het product waarbij deze taak hoort."),
    )

    class Meta:
        verbose_name = _("Taak")
        verbose_name_plural = _("Taken")
        unique_together = (("product", "uuid"),)

    def clean(self):
        check_externe_verwijzing_config_url("taken_url")

    def __str__(self):
        return str(self.uuid)
