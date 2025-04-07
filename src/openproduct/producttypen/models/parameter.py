from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel


@reversion.register()
class Parameter(BaseModel):

    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("De naam van de parameter."),
        validators=[RegexValidator(r"^[^:\[\]]+$")],
    )

    waarde = models.CharField(
        verbose_name=_("waarde"),
        max_length=255,
        help_text=_("De waarde van de parameter."),
        validators=[RegexValidator(r"^[^:\[\]]+$")],
    )

    producttype = models.ForeignKey(
        "ProductType",
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="parameters",
        help_text=_("Het producttype waarbij deze parameter hoort."),
    )

    class Meta:
        verbose_name = _("parameter")
        verbose_name_plural = _("parameters")
        unique_together = (("producttype", "naam"),)
        ordering = ("id",)

    def __str__(self):
        return f"{self.naam}: {self.waarde}"
