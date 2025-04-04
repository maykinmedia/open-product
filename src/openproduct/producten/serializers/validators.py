from django.core.exceptions import ValidationError

from rest_framework import serializers
from rest_framework.serializers import Serializer

from openproduct.producten.models.validators import (
    validate_eigenaar_identifier,
    validate_eigenaar_vestingsnummer_only_with_kvk,
    validate_product_dataobject,
    validate_product_dates,
    validate_product_eind_datum,
    validate_product_start_datum,
    validate_product_status,
    validate_product_verbruiksobject,
)
from openproduct.utils.serializers import get_from_serializer_data_or_instance


class EigenaarIdentifierValidator:
    requires_context = True

    def __call__(self, value, serializer):
        bsn = get_from_serializer_data_or_instance("bsn", value, serializer)
        kvk_nummer = get_from_serializer_data_or_instance(
            "kvk_nummer", value, serializer
        )
        klantnummer = get_from_serializer_data_or_instance(
            "klantnummer", value, serializer
        )
        try:
            validate_eigenaar_identifier(bsn, kvk_nummer, klantnummer)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)


class EigenaarVestigingsnummerValidator:
    requires_context = True

    def __call__(self, value, serializer):
        kvk_nummer = get_from_serializer_data_or_instance(
            "kvk_nummer", value, serializer
        )
        vestigingsnummer = get_from_serializer_data_or_instance(
            "vestigingsnummer", value, serializer
        )
        try:
            validate_eigenaar_vestingsnummer_only_with_kvk(kvk_nummer, vestigingsnummer)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


def get_from_serializer_data_or_instance_and_changed(
    field: str, data: dict, serializer: Serializer
):
    value = get_from_serializer_data_or_instance(field, data, serializer)
    changed = data.get(field) is not None and (
        serializer.instance is None
        or data.get(field) != getattr(serializer.instance, field)
    )
    return value, changed


class StatusValidator:
    requires_context = True

    def __call__(self, value, serializer):
        status, status_changed = get_from_serializer_data_or_instance_and_changed(
            "status", value, serializer
        )
        producttype, producttype_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "producttype", value, serializer
            )
        )

        try:
            if status_changed or producttype_changed:
                validate_product_status(status, producttype)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class DateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        start_datum, start_datum_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "start_datum", value, serializer
            )
        )
        eind_datum, eind_datum_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "eind_datum", value, serializer
            )
        )
        producttype, producttype_changed = (
            get_from_serializer_data_or_instance_and_changed(
                "producttype", value, serializer
            )
        )
        try:
            if start_datum_changed or producttype_changed:
                validate_product_start_datum(start_datum, producttype)
            if eind_datum_changed or producttype_changed:
                validate_product_eind_datum(eind_datum, producttype)
            validate_product_dates(start_datum, eind_datum)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class VerbruiksObjectValidator:
    requires_context = True

    def __call__(self, value, serializer):
        verbruiksobject = get_from_serializer_data_or_instance(
            "verbruiksobject", value, serializer
        )
        producttype = get_from_serializer_data_or_instance(
            "producttype", value, serializer
        )
        try:
            validate_product_verbruiksobject(verbruiksobject, producttype)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class DataObjectValidator:
    requires_context = True

    def __call__(self, value, serializer):
        dataobject = get_from_serializer_data_or_instance(
            "dataobject", value, serializer
        )
        producttype = get_from_serializer_data_or_instance(
            "producttype", value, serializer
        )
        try:
            validate_product_dataobject(dataobject, producttype)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
