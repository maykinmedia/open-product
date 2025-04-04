from django.contrib import admin

from open_producten.producttypen.models import VerzoekType


class VerzoekTypeInline(admin.TabularInline):
    model = VerzoekType
    extra = 1
