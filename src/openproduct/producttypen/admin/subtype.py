from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import SubType
from openproduct.producttypen.models.validators import validate_subtypen


class SubTypeInlineFormSet(AuditLogInlineformset):
    def clean(self):
        super().clean()
        validate_subtypen(
            [
                form.cleaned_data.get("naam")
                for form in self.forms
                if form.cleaned_data and not self._should_delete_form(form)
            ]
        )


class SubTypeInline(admin.TabularInline):
    model = SubType
    formset = SubTypeInlineFormSet
    extra = 0
    fields = ("naam",)
