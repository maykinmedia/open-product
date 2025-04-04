from django.contrib import admin

from ordered_model.admin import OrderedInlineMixin
from parler.admin import TranslatableStackedInline
from parler.forms import TranslatableModelForm

from openproduct.producttypen.models import ContentElement, ContentLabel
from openproduct.utils.widgets import WysimarkWidget


@admin.register(ContentLabel)
class ContentLabelAdmin(admin.ModelAdmin):
    search_fields = ("naam",)


class ContentElementInlineForm(TranslatableModelForm):

    class Meta:
        model = ContentElement
        fields = "__all__"
        widgets = {"content": WysimarkWidget()}


class ContentElementInline(OrderedInlineMixin, TranslatableStackedInline):
    model = ContentElement
    readonly_fields = ("move_up_down_links",)
    ordering = ("order",)
    fields = ("move_up_down_links", "content", "labels")
    autocomplete_fields = ("labels",)
    extra = 1
    form = ContentElementInlineForm
