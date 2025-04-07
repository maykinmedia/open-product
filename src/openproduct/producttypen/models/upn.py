from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel


@reversion.register()
class UniformeProductNaam(BaseModel):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("Uniforme product naam"),
        unique=True,
    )

    uri = models.URLField(
        verbose_name=_("Uri"),
        help_text=_("Uri naar de UPN definitie."),
        unique=True,
    )
    is_verwijderd = models.BooleanField(
        _("is verwijderd"),
        help_text=_("Geeft aan of de UPN is verwijderd."),
        default=False,
    )

    class Meta:
        verbose_name = _("Uniforme product naam")
        verbose_name_plural = _("Uniforme product namen")
        ordering = ("id",)

    def __str__(self):
        return self.naam
