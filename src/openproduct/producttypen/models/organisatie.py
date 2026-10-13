from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.locaties.models import Organisatie

from .enums import OrganisatieRolChoices


@reversion.register()
class ProductTypeOrganisatie(models.Model):
    id = models.AutoField(primary_key=True)

    producttype = models.ForeignKey(
        "producttypen.ProductType",
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="producttype_organisaties",
    )
    organisatie = models.ForeignKey(
        Organisatie,
        verbose_name=_("organisatie"),
        on_delete=models.CASCADE,
        related_name="producttype_organisaties",
    )
    rol = models.CharField(
        verbose_name=_("rol"),
        max_length=255,
        choices=OrganisatieRolChoices.choices,
        blank=True,
        help_text=_("De rol van de organisatie binnen het producttype."),
    )

    class Meta:
        db_table = "producttypen_producttype_organisaties"
        verbose_name = _("Producttype organisatie")
        verbose_name_plural = _("Producttype organisaties")
        unique_together = (("producttype", "organisatie"),)

    def __str__(self):
        return f"{self.producttype} - {self.organisatie}"
