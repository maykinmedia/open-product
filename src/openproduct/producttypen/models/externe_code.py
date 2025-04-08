from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel


@reversion.register()
class ExterneCode(BaseModel):

    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("De naam van het systeem van de externe producttype code."),
        validators=[RegexValidator(r"^[^:\[\]]+$")],
    )

    code = models.CharField(
        verbose_name=_("code"),
        max_length=255,
        help_text=_("De code van het producttype in het externe systeem."),
        validators=[RegexValidator(r"^[^:\[\]]+$")],
    )

    producttype = models.ForeignKey(
        "ProductType",
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="externe_codes",
        help_text=_("Het producttype waarbij deze externe code hoort."),
    )

    class Meta:
        verbose_name = _("externe producttype code")
        verbose_name_plural = _("externe producttype codes")
        unique_together = (("producttype", "naam"),)
        ordering = ("-id",)

    def __str__(self):
        return f"{self.naam}: {self.code}"
