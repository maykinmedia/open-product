from django.contrib import admin

from ..models import Bestand


class BestandInline(admin.TabularInline):
    model = Bestand
    extra = 1


@admin.register(Bestand)
class BestandAdmin(admin.ModelAdmin):
    list_display = ("product_type", "bestand")
    list_filter = ("product_type",)
    search_fields = ("bestand",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")
