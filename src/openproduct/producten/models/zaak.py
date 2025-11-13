from django.db import models
from django.utils.translation import gettext_lazy as _

from ...urn.models import UrnAbstractModel
from .product import Product


class Zaak(UrnAbstractModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="zaken",
        on_delete=models.CASCADE,
        help_text=_("Het product waarbij deze zaak hoort."),
    )

    class Meta:
        verbose_name = _("Zaak")
        verbose_name_plural = _("Zaken")
        unique_together = (("product", "urn"), ("product", "url"))
        ordering = ("-id",)

    def __str__(self):
        return self.urn if self.urn else self.url
