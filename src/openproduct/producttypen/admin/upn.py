from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from ..models import UniformeProductNaam


@admin.register(UniformeProductNaam)
class UniformeProductNaamAdmin(CompareVersionAdmin):
    list_display = ("naam", "uri", "is_verwijderd")
    list_filter = ("is_verwijderd",)
    search_fields = ("naam", "uri")

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
