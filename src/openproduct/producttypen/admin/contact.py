from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import ProductTypeContact


class ProductTypeContactInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = ProductTypeContact
    autocomplete_fields = ("contact",)
    extra = 1
