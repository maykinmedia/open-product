from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import BaseInlineFormSet
from django.urls import reverse
from django.utils.translation import gettext

from furl import furl

from openproduct.accounts.models import User

from .logevent import (
    audit_admin_create,
    audit_admin_delete,
    audit_admin_read,
    audit_admin_update,
)
from .serializing import serialize_instance

__all__ = ["AdminAuditLogMixin", "AuditLogInlineformset"]


class AdminAuditLogMixin:
    """
    Enable audit logging in the admin.

    Add, change, delete and view action will be logged.
    """

    model: type[models.Model]

    def log_addition(self, request, object, message):
        assert isinstance(request.user, User)
        audit_admin_create(
            content_object=object,
            django_user=request.user,
            object_data=serialize_instance(object),
        )

        return super().log_addition(  # pyright: ignore[reportAttributeAccessIssue]
            request, object, message
        )

    def log_change(self, request, object, message):
        assert isinstance(request.user, User)
        audit_admin_update(
            content_object=object,
            django_user=request.user,
            object_data=serialize_instance(object),
        )

        return super().log_change(  # pyright: ignore[reportAttributeAccessIssue]
            request, object, message
        )

    def log_deletion(self, request, object, object_repr):
        assert isinstance(request.user, User)
        audit_admin_delete(
            content_object=object,
            django_user=request.user,
            object_data=serialize_instance(object),
        )

        return super().log_deletion(  # pyright: ignore[reportAttributeAccessIssue]
            request, object, object_repr
        )

    def change_view(
        self,
        request,
        object_id,
        form_url="",
        extra_context: dict[str, Any] | None = None,
    ):
        if object_id and request.method == "GET":
            object = self.model.objects.get(pk=object_id)

            if extra_context is None:
                extra_context = {}

            # extra context to render show logs button next to history button in change form
            audit_url, audit_label = get_logs_link(object)
            extra_context.update(
                {
                    "audit_log_url": audit_url,
                    "audit_log_label": audit_label,
                }
            )

            assert isinstance(request.user, User)
            audit_admin_read(content_object=object, django_user=request.user)

        return super().change_view(  # pyright: ignore[reportAttributeAccessIssue]
            request, object_id, form_url, extra_context
        )

    def get_formset_kwargs(self, request, obj, inline, prefix):
        kwargs = (
            super().get_formset_kwargs(  # pyright: ignore[reportAttributeAccessIssue]
                request, obj, inline, prefix
            )
        )
        kwargs["_django_user"] = request.user
        return kwargs


class AuditLogInlineformset(BaseInlineFormSet):
    """
    Custom formset class for admin inlines to enable audit logging.

    Add and update actions on related objects are logged.
    """

    def __init__(self, *args, **kwargs):
        self.django_user = kwargs.pop("_django_user", None)
        super().__init__(*args, **kwargs)

    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit)

        audit_admin_create(
            content_object=obj,
            django_user=self.django_user,
            object_data=serialize_instance(obj),
        )

        return obj

    def save_existing(self, form, obj, commit=True):
        audit_admin_update(
            content_object=obj,
            django_user=self.django_user,
            object_data=serialize_instance(obj),
        )

        return super().save_existing(form, obj, commit)

    def delete_existing(self, obj, commit=True):
        if commit:
            audit_admin_delete(
                content_object=obj,
                django_user=self.django_user,
                object_data=serialize_instance(obj),
            )

        super().delete_existing(obj, commit)


def get_logs_link(obj: models.Model) -> tuple[str, str]:
    """
    Return a tuple of ``url`` and ``label`` to display logs related to ``obj``.
    """
    path = reverse("admin:logging_timelinelogproxy_changelist")
    url = furl(path).add(
        {
            "content_type__exact": ContentType.objects.get_for_model(obj).pk,
            "object_id": obj.pk,
        }
    )
    return str(url), gettext("Show logs")
