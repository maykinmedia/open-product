from django.contrib import admin

from ..models import Locatie


@admin.register(Locatie)
class LocatieAdmin(admin.ModelAdmin):
    list_display = ("naam", "stad", "postcode", "straat", "huisnummer")
    list_filter = ("stad",)
    search_fields = ("naam", "stad", "postcode", "straat")
