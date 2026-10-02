from django import forms
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import append_meta
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": forms.CheckboxSelectMultiple,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


@extend_schema_field(OpenApiTypes.UUID)
class UUIDRelatedField(serializers.RelatedField):
    """
    A read-write field that represents the target of the relationship
    by a unique 'uuid' attribute.
    """

    default_error_messages = {
        "does_not_exist": _("Object with uuid={value} does not exist."),
        "invalid": _("Invalid value."),
    }

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        assert isinstance(queryset, QuerySet)
        try:
            return queryset.get(**{"uuid": data})
        except ObjectDoesNotExist:
            self.fail("does_not_exist", value=smart_str(data))
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, value):
        return getattr(value, "uuid")


class JSONObjectField(serializers.JSONField):
    """
    serializers.JSONField does not have a type by default and will show `any` in api spec.
    """


class JSONObjectFieldExtension(OpenApiSerializerFieldExtension):
    """
    Used instead of `extend_schema_field`, because that takes precedence over all field
    extensions, which would make more specific (higher priority) extensions impossible.
    """

    target_class = JSONObjectField
    priority = 0

    def map_serializer_field(self, auto_schema, direction):
        # extensions bypass the field meta (nullable, readOnly, etc.), so add it here
        return append_meta(
            {"type": "object", "additionalProperties": True},
            auto_schema._get_serializer_field_meta(self.target, direction),
        )
