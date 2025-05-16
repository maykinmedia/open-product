from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.utils.models import BaseModel

from ...producttypen.models import ExterneVerwijzingConfig
from ...producttypen.models.externeverwijzingconfig import VerwijzingTypes
from .product import Product


class Document(BaseModel):

    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        help_text=_("Uuid van het document."),
    )

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="documenten",
        on_delete=models.CASCADE,
        help_text=_("Het product waarbij dit document hoort."),
    )

    documenten_api = models.ForeignKey(
        ExterneVerwijzingConfig,
        limit_choices_to={"type": VerwijzingTypes.VERZOEKTYPEN},
        verbose_name=_("documenten api"),
        related_name="documenten",
        on_delete=models.PROTECT,
        help_text=_("de api waar dit document zich bevind."),
    )

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documenten")
        unique_together = (("product", "uuid"),)

    def __str__(self):
        return str(self.uuid)
