from typing import Type

from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openproduct.utils.serializers import clean_duplicate_uuids_in_list


class DuplicateIdValidator:
    requires_context = True

    def __init__(self, fields: list[str]):
        self.fields = fields

    def __call__(self, value, serializer):
        errors = dict()
        for field in self.fields:
            if serializer.initial_data.get(field):
                clean_duplicate_uuids_in_list(
                    serializer.initial_data[field], field, errors
                )

        if errors:
            raise serializers.ValidationError(errors)


class NestedObjectsValidator:
    requires_context = True

    def __init__(self, key: str, model: Type[models.Model]):
        self.key = key
        self.model = model

    def __call__(self, value, serializer):
        parent_instance = serializer.instance

        if not parent_instance or not value.get(self.key):
            return

        errors = []

        current_uuids = set(
            getattr(parent_instance, self.key).values_list("uuid", flat=True)
        )

        seen_uuids = set()

        for idx, obj in enumerate(value[self.key]):
            obj_uuid = obj.get("uuid", None)

            if not obj_uuid:
                continue

            if obj_uuid in current_uuids:

                if obj_uuid in seen_uuids:
                    errors.append(
                        _("Dubbel uuid: {} op index {}.").format(obj_uuid, idx)
                    )
                seen_uuids.add(obj_uuid)

            else:
                try:
                    self.model.objects.get(uuid=obj_uuid)

                    # If the object is not related to the parent object but does exist when querying the nested object model itself
                    # it means that the nested object is related to a different parent object. It is only allowed to related nested objects.
                    errors.append(
                        _(
                            "{} uuid {} op index {} is niet onderdeel van het {} object."
                        ).format(
                            self.model._meta.verbose_name,
                            obj_uuid,
                            idx,
                            parent_instance._meta.verbose_name,
                        )
                    )
                except self.model.DoesNotExist:
                    errors.append(
                        _("{} uuid {} op index {} bestaat niet.").format(
                            self.model._meta.verbose_name, obj_uuid, idx
                        )
                    )

        if errors:
            raise serializers.ValidationError({self.key: errors})
