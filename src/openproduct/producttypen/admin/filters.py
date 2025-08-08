from datetime import date

from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class GepubliceerdFilter(SimpleListFilter):
    title = "gepubliceerd"
    parameter_name = "gepubliceerd"

    def lookups(self, request, model_admin):
        return [("yes", _("Ja")), ("no", _("Nee"))]

    def queryset(self, request, queryset):
        if self.value() not in ("yes", "no"):
            return queryset
        today = date.today()
        expr = Q(
            publicatie_start_datum__isnull=False, publicatie_start_datum__lte=today
        ) & (Q(publicatie_eind_datum__isnull=True) | Q(publicatie_eind_datum__gt=today))
        return (
            queryset.filter(expr) if self.value() == "yes" else queryset.exclude(expr)
        )
