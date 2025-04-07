from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.models import BaseModel
from openproduct.utils.validators import validate_phone_number, validate_postal_code


class BaseLocatie(BaseModel):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
    )
    email = models.EmailField(
        verbose_name=_("email adres"),
        blank=True,
    )
    telefoonnummer = models.CharField(
        verbose_name=_("telefoonnummer"),
        blank=True,
        max_length=15,
        validators=[validate_phone_number],
    )

    straat = models.CharField(_("straat"), blank=True, max_length=255)
    huisnummer = models.CharField(
        _("huisnummer"),
        blank=True,
        max_length=10,
    )

    postcode = models.CharField(
        _("postcode"),
        max_length=7,
        validators=[validate_postal_code],
        blank=True,
    )
    stad = models.CharField(
        _("stad"),
        max_length=255,
        blank=True,
    )

    class Meta:
        abstract = True

    @property
    def address(self) -> str:
        postcode = self.postcode.replace(" ", "")
        return f"{self.straat} {self.huisnummer}, {postcode} {self.stad}"


@reversion.register()
class Locatie(BaseLocatie):
    class Meta:
        verbose_name = _("Locatie")
        verbose_name_plural = _("Locaties")
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.naam}: {self.address}"
