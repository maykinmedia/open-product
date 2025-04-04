from django.contrib import admin

from openproduct.producttypen.models import VerzoekType


class VerzoekTypeInline(admin.TabularInline):
    model = VerzoekType
    extra = 1
