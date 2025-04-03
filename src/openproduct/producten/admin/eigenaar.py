from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producten.models import Eigenaar


class EigenaarInlineFormSet(AuditLogInlineformset):

    def clean(self):
        """Check that at least one eigenaar has been added."""
        super().clean()
        if any(self.errors):
            return
        if not any(
            cleaned_data and not cleaned_data.get("DELETE", False)
            for cleaned_data in self.cleaned_data
        ):
            raise ValidationError(_("Er is minimaal één eigenaar vereist."))


class EigenaarInline(admin.TabularInline):
    formset = EigenaarInlineFormSet
    model = Eigenaar
    extra = 1
