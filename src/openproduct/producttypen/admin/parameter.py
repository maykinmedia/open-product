from django.contrib import admin

from openproduct.producttypen.models import Parameter


class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 1
    ordering = ("pk",)
