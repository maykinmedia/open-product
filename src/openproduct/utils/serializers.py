from uuid import UUID

from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers
from rest_framework.serializers import Serializer

from .models import BaseModel


def get_from_serializer_data_or_instance(
    field: str, data: dict, serializer: Serializer
):
    if field in data:
        return data[field]

    if serializer.instance:
        return getattr(serializer.instance, field)


def clean_duplicate_uuids_in_list(values: list, field: str, errors):
    value_set = set()
    errors_messages = []
    for idx, value in enumerate(values):
        if value in value_set:
            errors_messages.append(_("Dubbel uuid: {} op index {}.").format(value, idx))

        value_set.add(value)

    if errors_messages:
        errors[field] = errors_messages


def model_to_dict_with_related_ids(model: BaseModel) -> dict:
    """Creates a dict from a model and appends UUID fields with '_id'"""
    model_dict = model_to_dict(model)

    for k, v in list(model_dict.items()):
        if isinstance(v, UUID):
            model_dict[f"{k}_id"] = model_dict.pop(k)

    return model_dict


def set_nested_serializer(data: list[dict], serializer: type[Serializer]):
    serializer_instance = serializer(
        data=data,
        many=True,
    )
    serializer_instance.is_valid(raise_exception=True)
    serializer_instance.save()


def validate_key_value_model_keys(
    data_list: list[dict], unique_field: str, error_message: str
):
    seen = set()

    for data in data_list:
        if data[unique_field] in seen:
            raise serializers.ValidationError(
                error_message.format(data[unique_field]), code="unique"
            )
        seen.add(data[unique_field])

    return data_list


class DetailErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Bad request example",
            description="Errors worden per veld teruggegeven.",
            value={
                "veld_a": "Dit veld is vereist.",
                "veld_b": "‘<uuid>’ is geen geldige UUID.",
            },
        ),
    ]
)
class ErrorSerializer(serializers.Serializer):
    veld_a = serializers.ListField(child=serializers.CharField())
    veld_b = serializers.ListField(child=serializers.CharField())
