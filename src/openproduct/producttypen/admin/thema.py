from django import forms
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from reversion_compare.admin import CompareVersionAdmin

from openproduct.utils.widgets import WysimarkWidget

from ...logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from ..models import ProductType, Thema


class ProductTypeInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = ProductType.themas.through
    extra = 0

    verbose_name = _("producttype")
    verbose_name_plural = _("Producttypen")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class ThemaAdminForm(forms.ModelForm):
    class Meta:
        model = Thema
        fields = "__all__"
        widgets = {"beschrijving": WysimarkWidget()}


@admin.register(Thema)
class ThemaAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    inlines = (ProductTypeInline,)
    search_fields = ("naam", "hoofd_thema__naam")
    list_display = ("naam", "hoofd_thema", "gepubliceerd", "producttypen_count")
    form = ThemaAdminForm

    @admin.display(description=_("Aantal producttypen"))
    def producttypen_count(self, obj):
        return obj.producttypen_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(producttypen_count=Count("producttypen"))
        return queryset

    list_filter = ["gepubliceerd", "producttypen", "hoofd_thema"]

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
