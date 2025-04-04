from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producten.models import Document


class DocumentInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Document
    extra = 1
