from django.contrib import admin

from openproduct.producttypen.models import ProductTypePermission


@admin.register(ProductTypePermission)
class ProductTypePermissionAdmin(admin.ModelAdmin):
    pass
