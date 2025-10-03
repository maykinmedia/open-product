from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.urn.fields import BaseUrnField


class UrnMappingConfig(models.Model):
    urn = BaseUrnField(verbose_name=_("Urn"), help_text=_("Urn"), unique=True)

    url = models.URLField(
        verbose_name=_("basis url"),
        help_text=_("Basis url van een urn."),
        unique=True,
    )

    class Meta:
        verbose_name = _("Urn Mapping")
        verbose_name_plural = _("Urn Mappings")

    def __str__(self):
        return f"{self.urn}: {self.url}"
