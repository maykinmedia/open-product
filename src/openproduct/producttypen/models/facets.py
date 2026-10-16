from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.producttypen.models.validators import (
    check_meervoudig_facettype,
    check_verplicht_facettype,
)
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
        default=True,
        help_text=_("Geeft aan of er kan worden gefiltered op het facet"),
    )
    meervoudig_toegestaan = models.BooleanField(
        _("meervoudig toegestaan"),
        default=False,
        help_text=_(
            "Geeft aan of een facet meerdere keren mag voorkomen op het producttype"
        ),
    )
    verplicht = models.BooleanField(
        _("verplicht"),
        default=False,
        help_text=_(
            "Geeft aan of het facet verplicht is voor producttype. Een facet kan alleen verplicht worden als alle bestaande producttype een waarde hebben."
        ),
    )

    class Meta:
        verbose_name = _("facettype")
        verbose_name_plural = _("facettypen")
        ordering = ("naam",)

    def __str__(self):
        return self.naam

    def clean(self):
        super().clean()
        check_meervoudig_facettype(self, self.meervoudig_toegestaan)
        check_verplicht_facettype(self, self.verplicht)


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
        help_text=_("Geeft aan of de facet waarde actief is"),
    )

    class Meta:
        verbose_name = _("facetwaarde")
        verbose_name_plural = _("facetwaarden")
        ordering = ("naam",)

    def __str__(self):
        return f"{self.facet_type.naam}: {self.naam}"


class ProductTypeFacet(models.Model):
    producttype = models.ForeignKey(
        "producttypen.ProductType",
        on_delete=models.CASCADE,
        related_name="ProductType_facetten+",
        verbose_name=_("producttype"),
    )
    facetwaarde = models.ForeignKey(
        FacetWaarde,
        on_delete=models.CASCADE,
        related_name="ProductType_facetten+",
        verbose_name=_("facetwaarde"),
    )

    class Meta:
        db_table = "producttypen_producttype_facetten"
        verbose_name = _("facet")
        verbose_name_plural = _("facetten")
        ordering = ("facetwaarde__facet_type__naam", "facetwaarde__naam")
        unique_together = ("producttype", "facetwaarde")

    def __str__(self):
        return f"{str(self.producttype)}: {str(self.facetwaarde)}"
