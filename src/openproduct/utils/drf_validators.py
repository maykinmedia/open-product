from typing import Type

from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openproduct.utils.serializers import clean_duplicate_ids_in_list


class DuplicateIdValidator:
    requires_context = True

    def __init__(self, fields: list[str]):
        self.fields = fields

    def __call__(self, value, serializer):
        errors = dict()
        for field in self.fields:
            if serializer.initial_data.get(field):
                clean_duplicate_ids_in_list(
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

        current_ids = set(
            getattr(parent_instance, self.key).values_list("id", flat=True)
        )

        seen_ids = set()

        for idx, obj in enumerate(value[self.key]):
            obj_id = obj.get("id", None)

            if not obj_id:
                continue

            if obj_id in current_ids:

                if obj_id in seen_ids:
                    errors.append(_("Dubbel id: {} op index {}.").format(obj_id, idx))
                seen_ids.add(obj_id)

            else:
                try:
                    self.model.objects.get(id=obj_id)

                    # If the object is not related to the parent object but does exist when querying the nested object model itself
                    # it means that the nested object is related to a different parent object. It is only allowed to related nested objects.
                    errors.append(
                        _(
                            "{} id {} op index {} is niet onderdeel van het {} object."
                        ).format(
                            self.model._meta.verbose_name,
                            obj_id,
                            idx,
                            parent_instance._meta.verbose_name,
                        )
                    )
                except self.model.DoesNotExist:
                    errors.append(
                        _("{} id {} op index {} bestaat niet.").format(
                            self.model._meta.verbose_name, obj_id, idx
                        )
                    )

        if errors:
            raise serializers.ValidationError({self.key: errors})
