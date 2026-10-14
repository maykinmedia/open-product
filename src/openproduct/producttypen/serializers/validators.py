from django.core.exceptions import ValidationError
from django.db import models

from rest_framework import serializers

from ...utils.serializers import get_from_serializer_data_or_instance
from ..models.validators import (
    check_for_circular_reference,
    check_meervoudig_facettype,
    check_subtypen_delete,
    check_verplicht_facettype,
    check_verplichte_facetwaarden_delete,
    validate_actie_direct_url,
    validate_actie_dmn,
    validate_actie_mapping,
    validate_actie_method,
    validate_exactly_one_producttype_or_thema,
    validate_prijs_optie_xor_regel,
    validate_publicatie_dates,
    validate_subtypen,
    validate_thema_gepubliceerd_state,
    validate_uniforme_product_naam_constraint,
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


class FacetTypeMeervoudigValidator:
    requires_context = True

    def __call__(self, value, serializer):
        meervoudig_toegestaan = get_from_serializer_data_or_instance(
            "meervoudig_toegestaan", value, serializer
        )
        try:
            check_meervoudig_facettype(serializer.instance, meervoudig_toegestaan)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class FacetTypeVerplichtValidator:
    requires_context = True

    def __call__(self, value, serializer):
        verplicht = get_from_serializer_data_or_instance("verplicht", value, serializer)
        try:
            check_verplicht_facettype(serializer.instance, verplicht)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class FacetWaardenDeleteValidator:
    requires_context = True

    def __call__(self, value, serializer):
        facet_type = serializer.instance
        if not facet_type or "waarden" not in value:
            return

        kept_uuids = {waarde["uuid"] for waarde in value["waarden"] if "uuid" in waarde}
        removed = list(facet_type.waarden.exclude(uuid__in=kept_uuids))
        verplicht = get_from_serializer_data_or_instance("verplicht", value, serializer)

        try:
            check_verplichte_facetwaarden_delete(facet_type, removed, verplicht)
        except ValidationError as e:
            raise serializers.ValidationError({"waarden": e.messages})


class SubTypenValidator:
    requires_context = True

    def __call__(self, value, serializer):
        if "subtypen" not in value:
            return

        subtypen = value["subtypen"]
        try:
            validate_subtypen([subtype.get("naam") for subtype in subtypen])
            if serializer.instance:
                check_subtypen_delete(
                    serializer.instance,
                    {subtype["uuid"] for subtype in subtypen if "uuid" in subtype},
                )
        except ValidationError as e:
            raise serializers.ValidationError({"subtypen": e.messages})


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
            raise serializers.ValidationError(e.message_dict)


class DoelgroepUplValidator:
    requires_context = True

    def __call__(self, value, serializer):
        upl = get_from_serializer_data_or_instance(
            "uniforme_product_naam", value, serializer
        )

        doelgroep = get_from_serializer_data_or_instance("doelgroep", value, serializer)

        try:
            validate_uniforme_product_naam_constraint(upl, doelgroep)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class ContentElementProducttypeThemaValidator:
    requires_context = True

    def __call__(self, value, serializer):
        producttype = get_from_serializer_data_or_instance(
            "producttype", value, serializer
        )
        thema = get_from_serializer_data_or_instance("thema", value, serializer)

        validate_exactly_one_producttype_or_thema(
            producttype=producttype,
            thema=thema,
        )


class ActieValidator:
    requires_context = True

    def __call__(self, value, serializer):
        mapping = get_from_serializer_data_or_instance("mapping", value, serializer)
        method = get_from_serializer_data_or_instance("method", value, serializer)
        type = get_from_serializer_data_or_instance("type", value, serializer)
        direct_url = get_from_serializer_data_or_instance(
            "direct_url", value, serializer
        )
        dmn_config = get_from_serializer_data_or_instance(
            "dmn_config", value, serializer
        )
        dmn_tabel_id = get_from_serializer_data_or_instance(
            "dmn_tabel_id", value, serializer
        )

        try:
            validate_actie_mapping(mapping, type)
            validate_actie_direct_url(direct_url, type)
            validate_actie_method(method, type)
            validate_actie_dmn(dmn_config, dmn_tabel_id, type)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
