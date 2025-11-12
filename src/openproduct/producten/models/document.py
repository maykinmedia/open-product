from django.db import models
from django.utils.translation import gettext_lazy as _

from ...urn.models import UrnAbstractModel
from .product import Product


class Document(UrnAbstractModel):
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
        unique_together = (("product", "urn"), ("product", "url"))

    def __str__(self):
        return self.urn if self.urn else self.url
