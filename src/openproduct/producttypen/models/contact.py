from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from openproduct.locaties.models import Contact

from .enums import ContactRolChoices


@reversion.register()
class ProductTypeContact(models.Model):
    producttype = models.ForeignKey(
        "producttypen.ProductType",
        verbose_name=_("producttype"),
        on_delete=models.CASCADE,
        related_name="producttype_contacten",
    )
    contact = models.ForeignKey(
        Contact,
        verbose_name=_("contact"),
        on_delete=models.CASCADE,
        related_name="producttype_contacten",
    )
    rol = models.CharField(
        verbose_name=_("rol"),
        max_length=255,
        choices=ContactRolChoices.choices,
        blank=True,
        help_text=_("De rol van het contact binnen het producttype."),
    )

    class Meta:
        db_table = "producttypen_producttype_contacten"
        verbose_name = _("Producttype contact")
        verbose_name_plural = _("Producttype contacten")
        unique_together = (("producttype", "contact"),)

    def __str__(self):
        return f"{self.producttype} - {self.contact}"
