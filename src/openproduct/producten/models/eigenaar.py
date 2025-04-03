from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.producten.models.validators import (
    validate_bsn,
    validate_eigenaar_identifier,
    validate_eigenaar_vestingsnummer_only_with_kvk,
)
from openproduct.utils.models import BaseModel

from .product import Product


class Eigenaar(BaseModel):

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="eigenaren",
        on_delete=models.CASCADE,
        help_text=_("De organisatie van het contact"),
    )

    bsn = models.CharField(
        _("Burgerservicenummer"),
        help_text=_(
            "Het BSN van de product eigenaar, BSN van 8 karakters moet met een extra 0 beginnen."
        ),
        validators=[validate_bsn],
        blank=True,
    )

    kvk_nummer = models.CharField(
        _("KVK nummer"),
        help_text=_("Het kvk nummer van de product eigenaar"),
        max_length=8,
        validators=[MinLengthValidator(8), RegexValidator("^[0-9]*$")],
        blank=True,
    )

    vestigingsnummer = models.CharField(
        _("Vestigingsnummer"),
        max_length=24,
        blank=True,
        help_text=_("Een korte unieke aanduiding van een vestiging."),
    )

    klantnummer = models.CharField(
        _("Klantnummer"),
        help_text=_("generiek veld voor de identificatie van een klant."),
        max_length=50,
        blank=True,
    )

    def clean(self):
        validate_eigenaar_vestingsnummer_only_with_kvk(
            self.kvk_nummer, self.vestigingsnummer
        )
        validate_eigenaar_identifier(self.bsn, self.kvk_nummer, self.klantnummer)

    def __str__(self):
        if self.bsn:
            return f"BSN {self.bsn}"

        if self.klantnummer:
            return f"klantnummer {self.klantnummer}"

        if self.kvk_nummer:
            return f"KVK {self.kvk_nummer}" + (
                f" vestigingsnummer {self.vestigingsnummer}"
                if self.vestigingsnummer
                else ""
            )

    class Meta:
        verbose_name = _("Eigenaar")
        verbose_name_plural = _("Eigenaren")
