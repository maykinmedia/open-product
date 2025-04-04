from django.contrib import admin

from openproduct.producttypen.models import ZaakType


class ZaakTypeInline(admin.TabularInline):
    model = ZaakType
    extra = 1
