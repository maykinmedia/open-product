from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel


class DmnConfig(BaseModel):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("naam van de dmn instantie."),
    )

    tabel_endpoint = models.URLField(
        _("url"), help_text=_("basis endpoint voor de dmn tabellen."), unique=True
    )

    def __str__(self):
        return f"{self.naam} {self.tabel_endpoint}"

    class Meta:
        verbose_name = _("DMN configuratie")
        verbose_name_plural = _("DMN configuraties")
