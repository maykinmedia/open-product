import json

from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from django_celery_beat.admin import PeriodicTaskAdmin as _PeriodicTaskAdmin
from django_celery_beat.models import PeriodicTask

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
        return redirect(request.META.get("HTTP_REFERER", reverse("admin:index")))

    def detail_url(self, instance):
        url = reverse("admin:run_task", kwargs={"task_id": instance.pk})
        response = format_html(
            "<a class='button' href={url}>{label}</a>", url=url, label=_("Start taak")
        )
        return response


admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, PeriodicTaskAdmin)
