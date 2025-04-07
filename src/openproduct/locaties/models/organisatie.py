from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from .locatie import BaseLocatie


@reversion.register()
class Organisatie(BaseLocatie):
    class Meta:
        verbose_name = _("Organisatie")
        verbose_name_plural = _("Organisaties")
        ordering = ("id",)

    code = models.CharField(
        verbose_name=_("code"),
        max_length=255,
        help_text=_("code van de organisatie."),
        unique=True,
    )

    def __str__(self):
        return f"{self.naam}"
