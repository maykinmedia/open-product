from django import forms
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ordered_model.admin import OrderedInlineModelAdminMixin
from reversion_compare.admin import CompareVersionAdmin

from openproduct.utils.widgets import WysimarkWidget

from ...logging.admin_tools import AdminAuditLogMixin
from ..models import ProductType, Thema
from .content import ContentElementInline


class ThemaAdminForm(forms.ModelForm):
    class Meta:
        model = Thema
        fields = "__all__"
        widgets = {"beschrijving": WysimarkWidget()}


@admin.register(Thema)
class ThemaAdmin(OrderedInlineModelAdminMixin, AdminAuditLogMixin, CompareVersionAdmin):
    inlines = (ContentElementInline,)

    list_display = (
        "naam",
        "hoofd_thema",
        "gepubliceerd",
        "producttypen_count",
        "content_elementen_count",
    )
    list_filter = ["gepubliceerd", "producttypen", "hoofd_thema"]
    search_fields = ("naam", "hoofd_thema")
    form = ThemaAdminForm

    readonly_fields = ("uuid",)

    @admin.display(description=_("Aantal producttypen"))
    def producttypen_count(self, obj):
        return obj.producttypen_count

    @admin.display(description=_("Aantal content elementen"))
    def content_elementen_count(self, obj):
        return obj.content_elementen_count

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .annotate(
                producttypen_count=Count("producttypen"),
                content_elementen_count=Count("content_elementen", distinct=True),
            )
            .select_related("hoofd_thema")
        )
        return queryset

    def get_deleted_objects(self, objs, request):
        """
        Producttypen need at least one thema.
        """

        def get_producttype_url(instance):
            return reverse("admin:producttypen_producttype_change", args=(instance.id,))

        def get_current_producttype_themas(instance):
            return ", ".join(instance.themas.values_list("naam", flat=True))

        errors = []
        for producttype in ProductType.objects.filter(themas__in=objs).distinct():
            if producttype.themas.count() <= objs.count():
                errors.append(
                    format_html(
                        "Producttype <a href='{}'>{}</a> moet aan een minimaal één thema zijn gelinkt. Huidige thema's: {}.",
                        get_producttype_url(producttype),
                        producttype,
                        get_current_producttype_themas(producttype),
                    )
                )
        if errors:
            return [], [], [], errors
        return super().get_deleted_objects(objs, request)
