from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.producttypen.models.validators import (
    check_externe_verwijzing_config_url,
)
from openproduct.utils.models import BaseModel

from .product import Product


class Document(BaseModel):

    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        null=True,
        blank=True,
        help_text=_("Uuid van het document."),
    )

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="documenten",
        on_delete=models.CASCADE,
        help_text=_("Het product waarbij dit document hoort."),
    )

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documenten")
        unique_together = (("product", "uuid"),)

    def clean(self):
        check_externe_verwijzing_config_url("documenten_url")

    def __str__(self):
        return str(self.uuid)
