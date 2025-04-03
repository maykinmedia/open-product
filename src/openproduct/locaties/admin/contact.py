from django.contrib import admin

from ..models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("__str__", "organisatie")
    list_filter = ("organisatie", "organisatie__stad")
    search_fields = ("voornaam", "achternaam", "organisatie__naam")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("organisatie")
