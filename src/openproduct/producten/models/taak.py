from django.db import models
from django.utils.translation import gettext_lazy as _

from ...urn.models import UrnAbstractModel
from .product import Product


class Taak(UrnAbstractModel):
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
        unique_together = (("product", "urn"), ("product", "url"))
        ordering = ("-id",)

    def __str__(self):
        return self.urn if self.urn else self.url
