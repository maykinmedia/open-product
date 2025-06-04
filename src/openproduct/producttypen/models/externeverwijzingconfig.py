from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class ExterneVerwijzingConfig(SingletonModel):
    zaaktypen_url = models.URLField(
        verbose_name=_("Zaaktypen API url"),
        help_text=_("Basis url van Zaaktypen API."),
        blank=True,
    )
    processen_url = models.URLField(
        verbose_name=_("processen url"),
        help_text=_("Basis url van processen."),
        blank=True,
    )
    verzoektypen_url = models.URLField(
        verbose_name=_("verzoektypen url"),
        help_text=_("Basis url van verzoektypen."),
        blank=True,
    )

    documenten_url = models.URLField(
        verbose_name=_("Documenten API url"),
        help_text=_("Basis url van Documenten API."),
        blank=True,
    )

    zaken_url = models.URLField(
        verbose_name=_("Zaken API url"),
        help_text=_("Basis url van Zaken API."),
        blank=True,
    )

    taken_url = models.URLField(
        verbose_name=_("Taken API url"),
        help_text=_("Basis url van Taken API."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Externe verwijzingen configuratie")
