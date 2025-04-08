from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.utils.validators import validate_phone_number

from ...utils.models import BaseModel
from .organisatie import Organisatie


@reversion.register(follow=("organisatie",))
class Contact(BaseModel):
    organisatie = models.ForeignKey(
        Organisatie,
        verbose_name=_("organisatie"),
        null=True,
        blank=True,
        related_name="product_contacten",
        on_delete=models.SET_NULL,
        help_text=_("De organisatie van het contact"),
    )
    voornaam = models.CharField(
        verbose_name=_("voornaam"),
        max_length=255,
        help_text=_("voornaam van het contact"),
    )
    achternaam = models.CharField(
        verbose_name=_("achternaam"),
        max_length=255,
        help_text=_("achternaam van het contact"),
    )
    email = models.EmailField(
        verbose_name=_("email adres"),
        blank=True,
        help_text=_("email van het contact"),
    )
    telefoonnummer = models.CharField(
        verbose_name=_("telefoonnummer"),
        blank=True,
        max_length=15,
        validators=[validate_phone_number],
        help_text=_("telefoonnummer van het contact"),
    )
    rol = models.CharField(
        verbose_name=_("rol"),
        blank=True,
        max_length=100,
        help_text=_("De rol/functie van het contact"),
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacten")
        ordering = ("-id",)

    def __str__(self):
        if self.organisatie:
            return f"{self.voornaam} {self.achternaam} ({self.organisatie.naam})"
        return f"{self.voornaam} {self.achternaam}"

    def get_email(self):
        if self.email:
            return self.email
        return self.organisatie.email

    def get_phone_number(self):
        if self.telefoonnummer:
            return self.telefoonnummer
        return self.organisatie.telefoonnummer
