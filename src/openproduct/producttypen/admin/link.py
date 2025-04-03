from django.contrib import admin

from ..models import Link


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1
    ordering = ("pk",)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("product_type", "naam", "url")
    list_filter = ("product_type__code",)
    search_fields = ("naam", "product_type__translations__naam")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")
