from django.contrib import admin
from django.urls import reverse

from ordered_model.admin import OrderedInlineMixin
from parler.admin import TranslatableStackedInline
from parler.forms import TranslatableBaseInlineFormSet, TranslatableModelForm
from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from openproduct.producttypen.models import (
    ContentElement,
    ContentElementTranslation,
    ContentLabel,
)
from openproduct.utils.widgets import WysimarkWidget


@admin.register(ContentLabel)
class ContentLabelAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    search_fields = ("naam",)


@admin.register(ContentElementTranslation)
class ContentElementTranslationAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("contentelement", "language_code")
    list_filter = ("master__producttype", "master__labels", "language_code")
    search_fields = ("master__producttype", "master__labels")
    readonly_fields = ("master", "language_code")

    @admin.display(description="contentelement")
    def contentelement(self, obj):
        return obj.master

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Translations should only be deleted by the cascade on the producttype contentelement and not by themselves.
        When a producttype is deleted via the admin this function is still called and should return True.
        """
        if reverse("admin:producttypen_producttype_changelist") in request.path:
            return True

        return False


class ContentElementInlineForm(TranslatableModelForm):
    class Meta:
        model = ContentElement
        fields = "__all__"
        widgets = {"content": WysimarkWidget()}


class ContentElementInlineFormset(AuditLogInlineformset, TranslatableBaseInlineFormSet):
    pass


class ContentElementInline(OrderedInlineMixin, TranslatableStackedInline):
    model = ContentElement
    readonly_fields = ("move_up_down_links",)
    ordering = ("order",)
    fields = ("move_up_down_links", "content", "labels")
    autocomplete_fields = ("labels",)
    extra = 1
    form = ContentElementInlineForm
    formset = AuditLogInlineformset
