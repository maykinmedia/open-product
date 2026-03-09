import json
from dataclasses import asdict

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from openproduct.config.models import ReferentielijstenConfig


@admin.register(ReferentielijstenConfig)
class ReferentielijstenConfigAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "enabled",
                    "service",
                    "kanalen_tabel_code",
                    "get_connection_check",
                ),
            },
        ),
    )
    readonly_fields = ("get_connection_check",)

    @admin.display(description=_("Kanalen found for tabel code"))
    def get_connection_check(self, obj):
        if obj.pk is None:
            return _("n/a")

        result, status_code = obj.connection_check
        if isinstance(result, (dict, list)):
            pretty = json.dumps([asdict(t) for t in result], indent=2, default=str)
            return mark_safe(f"Status code: {status_code}<br><pre>{pretty}</pre>")
        return f"{status_code} - {result}" if status_code else result
