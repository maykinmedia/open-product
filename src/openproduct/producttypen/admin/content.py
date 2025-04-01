from django.contrib import admin

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
    list_display = ("master", "language_code")
    list_filter = ("master__product_type", "master__labels", "language_code")
    search_fields = ("master__product_type", "master__labels")
    readonly_fields = ("master", "language_code")


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
