from django.contrib import admin

from open_producten.producttypen.models import Proces


class ProcesInline(admin.TabularInline):
    model = Proces
    extra = 1
