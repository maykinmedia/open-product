from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.producttypen.models.validators import (
    disallow_hoofd_thema_self_reference,
    validate_thema_gepubliceerd_state,
)
from openproduct.utils.models import BasePublishableModel


@reversion.register(follow=("hoofd_thema",))
class Thema(BasePublishableModel):
    naam = models.CharField(
        verbose_name=_("naam"), max_length=255, help_text=_("Naam van het thema.")
    )

    hoofd_thema = models.ForeignKey(
        "self",
        verbose_name=_("hoofd thema"),
        help_text=_("Het hoofd thema van het thema."),
        related_name="sub_themas",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    beschrijving = models.TextField(
        verbose_name=_("beschrijving"),
        blank=True,
        default="",
        help_text=_("Beschrijving van het thema, ondersteund markdown format."),
    )

    class Meta:
        verbose_name = _("thema")
        verbose_name_plural = _("thema's")
        ordering = ("-id",)

    def __str__(self):
        return self.naam

    def clean(self):
        if self.pk:
            disallow_hoofd_thema_self_reference(self, self.hoofd_thema)

            validate_thema_gepubliceerd_state(
                self.hoofd_thema, self.gepubliceerd, self.sub_themas
            )
