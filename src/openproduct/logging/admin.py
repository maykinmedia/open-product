from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html, strip_tags
from django.utils.text import Truncator
from django.utils.translation import gettext, gettext_lazy as _

from timeline_logger.models import TimelineLog

from .constants import Events
from .models import TimelineLogProxy

admin.site.unregister(TimelineLog)


class EventListFilter(SimpleListFilter):
    title = _("event")
    parameter_name = "event"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
        return Events.choices

    def queryset(
        self, request: HttpRequest, queryset: models.QuerySet[TimelineLogProxy]
    ):
        if value := self.value():
            return queryset.filter(extra_data__event=value)
        return queryset


@admin.register(TimelineLogProxy)
class TimelineLogProxyAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "show_event",
        "show_content_type",
        "timestamp",
        "show_acting_user",
        "content_admin_link",
    )
    list_filter = ("timestamp", EventListFilter)
    ordering = ("-timestamp",)
    search_fields = (
        "extra_data__acting_user__identifier",
        "extra_data__acting_user__display_name",
        "extra_data___cached_object_repr",
    )
    list_select_related = ("content_type", "user")
    date_hierarchy = "timestamp"
    readonly_fields = ("get_message",)

    def has_add_permission(self, request: HttpRequest):
        # Not even superusers are allowed to make changes
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: TimelineLogProxy | None = None
    ):
        # Not even superusers are allowed to make changes
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: TimelineLogProxy | None = None
    ):
        # Not even superusers are allowed to make changes
        return False

    @admin.display(description=_("full log message"))
    def full_message(self, obj: TimelineLogProxy) -> str:
        return obj.get_message()

    @admin.display(description=_("message"))
    def message(self, obj: TimelineLogProxy) -> str:
        full_msg = strip_tags(self.full_message(obj))
        return Truncator(full_msg).chars(100) or gettext("(no message)")

    @admin.display(description=_("event"), ordering="extra_data__event")
    def show_event(self, obj: TimelineLogProxy) -> str:
        if (event := obj.event) == "unknown":
            return gettext("Unknown")
        return Events(event).label

    @admin.display(description=_("kind"), ordering="content_type")
    def show_content_type(self, obj: TimelineLogProxy) -> str | None:
        ct: ContentType | None = obj.content_type
        if ct is None:
            return None
        return ct.name

    @admin.display(description=_("acting user"))
    def show_acting_user(self, obj: TimelineLogProxy) -> str:
        acting_user, django_user = obj.acting_user
        format_str = (
            gettext("{name} ({identifier})")
            if not django_user
            else gettext("{name} ({identifier}, local user ID: {django_id})")
        )
        return format_str.format(
            name=acting_user["display_name"],
            identifier=acting_user["identifier"],
            django_id=django_user.pk if django_user else None,
        )

    @admin.display(description=_("affected object"))
    def content_admin_link(self, obj: TimelineLogProxy) -> str:
        if not (obj.object_id and obj.content_type_id):
            return "-"

        ct = obj.content_type
        obj_repr = obj.get_related_object_repr()
        try:
            admin_path = reverse(
                f"admin:{ct.app_label}_{ct.model}_change", args=(obj.object_id,)
            )
        except NoReverseMatch:  # content type not enabled in the admin
            return obj_repr
        return format_html('<a href="{u}">{t}</a>', u=admin_path, t=obj_repr)
