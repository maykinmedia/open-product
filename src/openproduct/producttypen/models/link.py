from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel

from .producttype import ProductType


@reversion.register(follow=("producttype",))
class Link(BaseModel):
    producttype = models.ForeignKey(
        ProductType,
        verbose_name=_("Producttype"),
        related_name="links",
        on_delete=models.CASCADE,
        help_text=_("Het producttype waarbij deze link hoort."),
    )
    naam = models.CharField(
        verbose_name=_("naam"), max_length=255, help_text=_("Naam van de link.")
    )
    url = models.URLField(verbose_name=_("Url"), help_text=_("Url van de link."))

    class Meta:
        verbose_name = _("Producttype link")
        verbose_name_plural = _("Producttype links")

    def __str__(self):
        return f"{self.producttype}: {self.naam}"
