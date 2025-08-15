from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid4, editable=False)

    class Meta:
        abstract = True


class BasePublishableModel(BaseModel):
    aanmaak_datum = models.DateTimeField(
        verbose_name=_("aanmaak datum"),
        auto_now_add=True,
        help_text=_("De datum waarop het object is aangemaakt."),
    )
    update_datum = models.DateTimeField(
        verbose_name=_("update datum"),
        auto_now=True,
        help_text=_("De datum waarop het object voor het laatst is gewijzigd."),
    )

    class Meta:
        abstract = True
