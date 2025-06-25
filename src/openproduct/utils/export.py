from django.contrib import admin, messages
from django.core.management import call_command
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.translation import gettext as _


def _create_file_response(name):
    response = HttpResponse(content_type="application/zip")
    filename = slugify(name)
    response["Content-Disposition"] = "attachment;filename={}".format(f"{filename}.zip")
    return response


def _call_export_command(modeladmin, response, ids, export_format):
    call_command(
        "export",
        modeladmin.opts.app_label,
        modeladmin.opts.model_name,
        response=response,
        ids=ids,
        format=export_format,
        exclude=modeladmin.export_exclude,
    )
    response["Content-Length"] = len(response.content)


def _export(modeladmin, request, queryset, export_format):
    model_name = modeladmin.model._meta.verbose_name_plural
    ids = list(queryset.values_list("pk", flat=True))

    response = _create_file_response(model_name)
    _call_export_command(modeladmin, response, ids, export_format)

    modeladmin.message_user(
        request,
        _("{} {} were successfully exported").format(len(ids), model_name),
        level=messages.SUCCESS,
    )
    return response


@admin.action(description="Export (CSV)")
def export_csv(modeladmin, request, queryset):
    _export(modeladmin, request, queryset, "csv")


@admin.action(description="Export (JSON)")
def export_json(modeladmin, request, queryset):
    _export(modeladmin, request, queryset, "json")


class ExportMixin:
    export_exclude = []

    def response_post_save_change(self, request, obj):
        if "_export" not in request.POST:
            return super().response_post_save_change(request, obj)

        # Clear messages
        for i in messages.get_messages(request):
            pass

        response = _create_file_response(str(obj))
        export_format = "csv" if "CSV" in request.POST["_export"] else "json"
        _call_export_command(self, response, [obj.id], export_format)

        self.message_user(
            request,
            _("{} {} was successfully exported").format(self.opts.model_name, obj),
            level=messages.SUCCESS,
        )
        return response
