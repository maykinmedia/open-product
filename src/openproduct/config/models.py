from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion
import structlog
from requests.exceptions import RequestException, Timeout
from rest_framework import status
from solo.models import SingletonModel
from zgw_consumers.models import Service

from .clients import get_referentielijsten_client

logger = structlog.get_logger(__name__)


@reversion.register()
class ReferentielijstenConfig(SingletonModel):
    enabled = models.BooleanField(
        default=False,
        help_text=_(
            "Indicates whether or not the optional Referentielijsten API integration is enabled"
        ),
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        help_text=_(
            "The service used to retrieve information from the Referentielijsten API"
        ),
    )
    kanalen_tabel_code = models.CharField(
        max_length=100,
        blank=True,
        help_text=_(
            "Code of the `tabel` that contains the possible `kanalen` (channels)"
        ),
    )

    def clean(self):
        if not self.enabled:
            return

        if not self.service:
            raise ValidationError(
                {
                    "service": _(
                        "Service moet zijn ingesteld wanneer validatie is ingeschakeld"
                    )
                }
            )

        if not self.kanalen_tabel_code:
            raise ValidationError(
                {
                    "kanalen_tabel_code": _(
                        "Kanalen moet zijn ingesteld wanneer validatie is ingeschakeld"
                    )
                }
            )

    def save(self, *args, **kwargs):
        # TODO here refresh the cache ?
        return super().save(*args, **kwargs)

    @property
    def connection_check(self):
        if not self.service or not self.kanalen_tabel_code:
            return _(
                "Not performing connection check, service and/or kanalen tabel code are not configured"
            ), None

        try:
            with get_referentielijsten_client(self) as client:
                if client.can_connect:
                    items = client.get_cached_items_by_tabel_code(
                        self.kanalen_tabel_code
                    )
                    return items, status.HTTP_200_OK
                return _("Unable to connect to Referentielijsten API"), None
        except Timeout:
            return _(
                "Request to Referentielijsten API timed out"
            ), status.HTTP_504_GATEWAY_TIMEOUT
        except RequestException:
            return _("Unable to retrieve items from Referentielijsten API"), None

    def __str__(self):
        return "Referentielijsten configuration"

    class Meta:
        verbose_name = _("Referentielijsten configuration")
