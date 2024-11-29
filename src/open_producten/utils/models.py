from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class BasePublishableModel(BaseModel):
    gepubliceerd = models.BooleanField(
        verbose_name=_("gepubliceerd"),
        default=False,
        help_text=_("Geeft aan of het object getoond kan worden."),
        # TODO unpublished objects are currently not filtered out of api.
    )
    aanmaak_datum = models.DateTimeField(
        verbose_name=_("Created on"),
        auto_now_add=True,
        help_text=_("De datum waarop het object is aangemaakt."),
    )
    update_datum = models.DateTimeField(
        verbose_name=_("Updated on"),
        auto_now=True,
        help_text=_("De datum waarop het object voor het laatst is gewijzigd."),
    )

    class Meta:
        abstract = True
