from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel


class FacetType(BaseModel):
    naam = models.CharField(
        _("naam"),
        max_length=255,
        help_text=_("Naam van het facet"),
    )
    omschrijving = models.TextField(
        _("omschrijving"),
        blank=True,
        help_text=_("Omschrijving van facet"),
    )
    facetteerbaar = models.BooleanField(
        _("facetteerbaar"),
        default=False,
        help_text=_("Kun je er op filteren, flexibiliteit!"),
    )
    meervoudig_toegestaan = models.BooleanField(
        _("meervoudig toegestaan"),
        default=False,
        help_text=_(
            "Kan facet meerdere keren voorkomen op producttype, bv doelgroepen"
        ),
    )
    verplicht = models.BooleanField(
        _("verplicht"),
        default=False,
        help_text=_("Verplicht voor producttype"),
    )

    class Meta:
        verbose_name = _("facettype")
        verbose_name_plural = _("facettypes")
        ordering = ("naam",)

    def __str__(self):
        return self.naam


class FacetWaarde(BaseModel):
    facet_type = models.ForeignKey(
        FacetType,
        on_delete=models.CASCADE,  # TODO check?
        related_name="waarden",
        verbose_name=_("facettype"),
    )
    naam = models.CharField(
        _("naam"),
        max_length=255,
    )
    omschrijving = models.TextField(
        _("omschrijving"),
        blank=True,
    )
    actief = models.BooleanField(
        _("actief"),
        default=True,
    )

    class Meta:
        verbose_name = _("facetwaarde")
        verbose_name_plural = _("facetwaarden")
        ordering = ("naam",)

    def __str__(self):
        return f"{self.facet_type.naam}: {self.naam}"
