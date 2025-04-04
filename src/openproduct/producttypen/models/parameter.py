from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel


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

    product_type = models.ForeignKey(
        "ProductType",
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="parameters",
        help_text=_("Het producttype waarbij deze parameter hoort."),
    )

    class Meta:
        verbose_name = _("parameter")
        verbose_name_plural = _("parameters")
        unique_together = (("product_type", "naam"),)
