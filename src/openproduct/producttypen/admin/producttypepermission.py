from django.contrib import admin

from openproduct.producttypen.models import ProductTypePermission


class ProductTypePermissionInline(admin.TabularInline):
    model = ProductTypePermission
    extra = 1
