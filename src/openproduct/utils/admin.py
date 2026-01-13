import json

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from django_celery_beat.admin import PeriodicTaskAdmin as _PeriodicTaskAdmin
from django_celery_beat.models import PeriodicTask
from parler.admin import TranslatableAdmin as _TranslatableAdmin

from openproduct.celery import app


class PeriodicTaskAdmin(_PeriodicTaskAdmin):
    list_display = _PeriodicTaskAdmin.list_display + ("detail_url",)

    def get_urls(self):
        urls = super().get_urls()
        return [path("<int:task_id>/run/", self.run_task, name="run_task")] + urls

    def run_task(self, request, task_id):
        periodic_task = get_object_or_404(self.model, pk=task_id)

        task_kwargs = json.loads(periodic_task.kwargs)
        task_args = json.loads(periodic_task.args)

        app.send_task(periodic_task.task, args=task_args, kwargs=task_kwargs)

        messages.success(request, f"Task '{periodic_task.name}' was sent to worker.")
        return redirect(reverse("admin:django_celery_beat_periodictask_changelist"))

    def detail_url(self, instance):
        url = reverse("admin:run_task", kwargs={"task_id": instance.pk})
        response = format_html(
            "<a class='button' href={url}>{label}</a>", url=url, label=_("Start taak")
        )
        return response


admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, PeriodicTaskAdmin)


class TranslatableAdmin(_TranslatableAdmin):
    """
    Parler adds a tab to the change view for each PARLER LANGUAGE. This made it possible to create a producttype without the dutch translation.

    This class overrides get_language_tabs so that only the NL tab is shown on create.
    """

    def get_language_tabs(self, request, obj, available_languages, css_class=None):
        tabs = super().get_language_tabs(request, obj, available_languages, css_class)

        if obj is None:
            tabs[:] = [tab for tab in tabs if settings.LANGUAGE_CODE in tab]

        return tabs


def user_model_search_fields_nl(field_names):
    User = get_user_model()
    search_fields = []
    help_texts = []

    for name in field_names:
        try:
            field = User._meta.get_field(name)
        except FieldDoesNotExist:
            continue
        else:
            search_fields.append(f"user__{field.name}")
            help_texts.append(str(field.verbose_name))

    if not help_texts:
        search_help_text = ""
    elif len(help_texts) == 1:
        search_help_text = _("Zoek op %(field)s") % {"field": help_texts[0]}
    else:
        search_help_text = _("Zoek op %(fields)s") % {
            "fields": _(", ").join(help_texts[:-1]) + _(" of ") + help_texts[-1]
        }

    return search_fields, search_help_text
