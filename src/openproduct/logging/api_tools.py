from typing import Generic, TypeVar

from django.db.models import Model

from rest_framework import serializers
from rest_framework.request import Request

from .logevent import (
    audit_api_create,
    audit_api_delete,
    audit_api_read,
    audit_api_update,
)
from .serializing import serialize_instance

__all__ = [
    "AuditTrailCreateMixin",
    "AuditTrailRetrieveMixin",
    "AuditTrailUpdateMixin",
    "AuditTrailDestroyMixin",
    "AuditTrailViewSetMixin",
    "extract_audit_parameters",
]

_MT_co = TypeVar("_MT_co", bound=Model, covariant=True)  # taken from DRF stubs


def extract_audit_parameters(request: Request) -> tuple[str, str, str]:
    user_id = request.user.id
    user_repr = request.user.username
    return user_id, user_repr, ""


class AuditTrailCreateMixin:
    """
    Add support for audit trails to the :class:`rest_framework.mixins.CreateModelMixin`.
    """

    request: Request

    def perform_create(self, serializer: serializers.BaseSerializer):
        super().perform_create(  # pyright: ignore[reportAttributeAccessIssue]
            serializer
        )

        instance = serializer.instance
        assert instance is not None

        user_id, user_repr, remarks = extract_audit_parameters(self.request)

        # XXX: there *could* be a django user making this request, and that information
        # is currently ignored
        audit_api_create(
            content_object=instance,
            user_id=user_id,
            user_display=user_repr,
            object_data=serialize_instance(instance),
            remarks=remarks,
        )


class AuditTrailRetrieveMixin(Generic[_MT_co]):
    """
    Add support for audit trails to the :class:`rest_framework.mixins.RetrieveModelMixin`.
    """

    _cached_object: _MT_co

    def get_object(self) -> _MT_co:
        # Optimize multiple calls to get_object, since the default implementations
        # performs the DB lookup and permission checks every time.
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object()  # pyright: ignore
        return self._cached_object

    def retrieve(self, request: Request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)  # pyright: ignore

        user_id, user_repr, remarks = extract_audit_parameters(request)
        audit_api_read(
            content_object=self.get_object(),
            user_id=user_id,
            user_display=user_repr,
            remarks=remarks,
        )

        return response


class AuditTrailUpdateMixin:
    """
    Add support for audit trails to the :class:`rest_framework.mixins.UpdateModelMixin`.
    """

    request: Request

    def perform_update(self, serializer: serializers.BaseSerializer):
        super().perform_update(  # pyright: ignore[reportAttributeAccessIssue]
            serializer
        )

        instance = serializer.instance
        assert instance is not None

        user_id, user_repr, remarks = extract_audit_parameters(self.request)
        audit_api_update(
            content_object=instance,
            user_id=user_id,
            user_display=user_repr,
            object_data=serialize_instance(instance),
            remarks=remarks,
        )


class AuditTrailDestroyMixin:
    """
    Add support for audit trails to the :class:`rest_framework.mixins.DestroyModelMixin`.
    """

    request: Request

    def perform_destroy(self, instance: Model):
        user_id, user_repr, remarks = extract_audit_parameters(self.request)

        # take a snapshot of the data before it's deleted by the super() method, that
        # way we can investigate if unintended deletes happen and start a manual
        # recovery procedure.
        audit_api_delete(
            content_object=instance,
            user_id=user_id,
            user_display=user_repr,
            object_data=serialize_instance(instance),
            remarks=remarks,
        )

        super().perform_destroy(instance)  # pyright: ignore[reportAttributeAccessIssue]


class AuditTrailViewSetMixin(
    AuditTrailCreateMixin,
    AuditTrailRetrieveMixin,
    AuditTrailUpdateMixin,
    AuditTrailDestroyMixin,
):
    """
    Add support for audit trails.

    This includes all the CRUD operations.
    """
