from django.contrib import admin

from openproduct.producttypen.models import Proces


class ProcesInline(admin.TabularInline):
    model = Proces
    extra = 1
