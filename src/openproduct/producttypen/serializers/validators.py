from django.core.exceptions import ValidationError
from django.db import models

from rest_framework import serializers

from ...utils.serializers import get_from_serializer_data_or_instance
from ..models.validators import (
    check_for_circular_reference,
    validate_prijs_optie_xor_regel,
    validate_publicatie_dates,
    validate_thema_gepubliceerd_state,
)


class ThemaGepubliceerdStateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        hoofd_thema = get_from_serializer_data_or_instance(
            "hoofd_thema", value, serializer
        )
        gepubliceerd = get_from_serializer_data_or_instance(
            "gepubliceerd", value, serializer
        )
        sub_themas = serializer.instance.sub_themas if serializer.instance else None

        try:
            validate_thema_gepubliceerd_state(hoofd_thema, gepubliceerd, sub_themas)
        except ValidationError as e:
            raise serializers.ValidationError({"hoofd_thema": e.message})


class ThemaReferenceValidator:
    requires_context = True

    def __call__(self, value, serializer):
        thema = serializer.instance
        hoofd_thema = get_from_serializer_data_or_instance(
            "hoofd_thema", value, serializer
        )

        try:
            check_for_circular_reference(thema, hoofd_thema)
        except ValidationError as e:
            raise serializers.ValidationError({"hoofd_thema": e.message})


class PrijsOptieRegelValidator:
    requires_context = True

    def __call__(self, value, serializer):
        opties = get_from_serializer_data_or_instance("prijsopties", value, serializer)
        regels = get_from_serializer_data_or_instance("prijsregels", value, serializer)
        try:
            validate_prijs_optie_xor_regel(get_count(opties), get_count(regels))
        except ValidationError as e:
            raise serializers.ValidationError({"opties_or_regels": e.message})


def get_count(obj: list | models.Manager | None):
    if obj is None:
        return 0
    if isinstance(obj, models.Manager):
        return obj.count()
    else:
        return len(obj)


class PublicatieDateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        pub_start_datum = get_from_serializer_data_or_instance(
            "publicatie_start_datum", value, serializer
        )

        pub_eind_datum = get_from_serializer_data_or_instance(
            "publicatie_eind_datum", value, serializer
        )
        try:
            validate_publicatie_dates(pub_start_datum, pub_eind_datum)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
