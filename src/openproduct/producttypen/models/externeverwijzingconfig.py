from django.db import models
from django.utils.translation import gettext_lazy as _


class VerwijzingTypes(models.TextChoices):
    DMN = "DMN", _("DMN")
    DOCUMENTEN = "documenten", _("Documenten")
    ZAAKTYPEN = "zaaktypen", _("Zaaktypen")
    PROCESSEN = "processen", _("Processen")
    VERZOEKTYPEN = "verzoektypen", _("Verzoektypen")

    # GH 134
    # TAKEN
    # ZAKEN


class ExterneVerwijzingConfig(models.Model):
    naam = models.CharField(
        verbose_name=_("naam"),
        max_length=255,
        help_text=_("naam van de externe verwijzing."),
        unique=True,
    )

    basis_url = models.URLField(
        verbose_name=_("basis url"),
        help_text=_("Basis url van van de externe verwijzing."),
        blank=True,
        unique=True,
    )

    type = models.CharField(
        verbose_name=_("type"),
        help_text=_("type van de externe verwijzing."),
        choices=VerwijzingTypes.choices,
    )

    class Meta:
        verbose_name = _("Externe verwijzingen configuratie")
        verbose_name_plural = _("Externe verwijzingen configuraties")
