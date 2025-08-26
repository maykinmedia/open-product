from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openproduct.urn.models import UrnMappingConfig


class UrnMappingMixin:
    urn_fields: list

    def validate(self, attrs):
        attrs = super().validate(attrs)

        for field in self.urn_fields:
            self.validate_field(field, attrs)

    def validate_field(self, field, attrs):
        urn_field = f"{field}_urn"
        url_field = f"{field}_url"

        urn, urn_uuid = self.get_base_and_uuid(attrs, urn_field, is_urn=True)
        url, url_uuid = self.get_base_and_uuid(attrs, url_field, is_urn=False)

        if not urn and not url:
            raise serializers.ValidationError(
                {field: _("een url of urn is verplicht")}
            )

        if urn_uuid and url_uuid and urn_uuid != url_uuid:
            raise serializers.ValidationError(
                {field: _("de uuid van de url en urn komen niet overeen")}
            )

        uuid = urn_uuid or url_uuid

        urn_mapping = (
            UrnMappingConfig.objects.filter(urn=urn).first() if urn else None
        )
        url_mapping = (
            UrnMappingConfig.objects.filter(url=url).first() if url else None
        )

        # Case: only URL
        if not urn:
            if url_mapping:
                attrs[urn_field] = f"{url_mapping.urn}:{uuid}"
            elif settings.REQUIRE_URL_URN_MAPPING:
                raise serializers.ValidationError(
                    {field: _("de url heeft geen mapping")}
                )

        # Case: only URN
        elif not url:
            if urn_mapping:
                attrs[url_field] = f"{urn_mapping.url}/{uuid}"
            elif settings.REQUIRE_URN_URL_MAPPING:
                raise serializers.ValidationError(
                    {field: _("de urn heeft geen mapping")}
                )

        # Case: both provided
        else:
            if not urn_mapping and not url_mapping:
                if (
                    settings.REQUIRE_URN_URL_MAPPING
                    or settings.REQUIRE_URL_URN_MAPPING
                ):
                    raise serializers.ValidationError(
                        {field: _("de url en/of urn hebben geen mapping")}
                    )
            elif urn_mapping and url_mapping:
                if urn_mapping != url_mapping:
                    raise serializers.ValidationError(
                        {field: _("de urn en url mappings komen niet overeen")}
                    )
            elif urn_mapping and not url_mapping:
                raise serializers.ValidationError(
                    {field: _("de url in de urn mapping is niet hetzelfde")}
                )
            elif url_mapping and not urn_mapping:
                raise serializers.ValidationError(
                    {field: _("de urn in de url mapping is niet hetzelfde")}
                )

        return attrs

    def get_base_and_uuid(
        self, attrs, field, is_urn=True
    ) -> tuple[str, str] | tuple[None, None]:
        sep = ":" if is_urn else "/"

        value = attrs.get(field) or getattr(self.instance, field, None)

        if value is None:
            return None, None
        return value.rsplit(sep, 1)


class RelatieListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        urns = getattr(data, f"{self.field_name}_urn", [])
        urls = getattr(data, f"{self.field_name}_url", [])
        max_len = max(len(urns), len(urls))

        relaties = []
        for i in range(max_len):
            relaties.append(
                {
                    "urn": urns[i] if i < len(urns) else None,
                    "url": urls[i] if i < len(urls) else None,
                }
            )
        return super().to_representation(relaties)

    def to_internal_value(self, data):
        ret = {f"{self.field_name}_urn": [], f"{self.field_name}_url": []}
        for relatie in data:
            ret[f"{self.field_name}_urn"].append(relatie.get("urn"))
            ret[f"{self.field_name}_url"].append(relatie.get("url"))

        return ret


class RelatieSerializer(serializers.Serializer):
    urn = serializers.CharField(required=False)
    url = serializers.CharField(required=False)

    class Meta:
        list_serializer_class = RelatieListSerializer
