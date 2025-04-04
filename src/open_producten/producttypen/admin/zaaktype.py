from django.contrib import admin

from open_producten.producttypen.models import ZaakType


class ZaakTypeInline(admin.TabularInline):
    model = ZaakType
    extra = 1
