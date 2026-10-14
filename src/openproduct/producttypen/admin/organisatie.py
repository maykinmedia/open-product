from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import ProductTypeOrganisatie


class ProductTypeOrganisatieInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = ProductTypeOrganisatie
    autocomplete_fields = ("organisatie",)
    extra = 1
