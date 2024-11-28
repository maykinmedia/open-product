from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import serializers

from open_producten.producttypen.models import (
    Onderwerp,
    ProductType,
    UniformeProductNaam,
)
from open_producten.utils.serializers import build_array_duplicates_error_message

from .children import VraagSerializer


class SimpleProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="uri", queryset=UniformeProductNaam.objects.all()
    )

    class Meta:
        model = ProductType
        exclude = (
            "onderwerpen",
            "organisaties",
            "locaties",
            "contacten",
        )


class OnderwerpSerializer(serializers.ModelSerializer):
    hoofd_onderwerp = serializers.PrimaryKeyRelatedField(
        queryset=Onderwerp.objects.all(),
        allow_null=True,
    )
    product_typen = SimpleProductTypeSerializer(many=True, read_only=True)
    vragen = VraagSerializer(many=True, read_only=True)

    product_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        default=[],
        write_only=True,
        source="product_typen",
    )

    class Meta:
        model = Onderwerp
        exclude = ("path", "depth", "numchild")

    def _handle_relations(self, instance, product_typen: list[ProductType]):
        errors = dict()
        if product_typen is not None:
            build_array_duplicates_error_message(
                product_typen, "product_type_ids", errors
            )
            instance.product_typen.set(product_typen)

        if errors:
            raise serializers.ValidationError(errors)

    def _validate_onderwerp(self, onderwerp):
        try:
            onderwerp.clean()
        except ValidationError as err:
            raise serializers.ValidationError({"hoofd_onderwerp": err.message})

    @transaction.atomic()
    def create(self, validated_data):
        product_typen = validated_data.pop("product_typen")
        hoofd_onderwerp = validated_data.pop("hoofd_onderwerp")

        if hoofd_onderwerp:
            onderwerp = hoofd_onderwerp.add_child(**validated_data)
        else:
            onderwerp = Onderwerp.add_root(**validated_data)

        self._validate_onderwerp(onderwerp)
        self._handle_relations(onderwerp, product_typen)
        onderwerp.save()

        return onderwerp

    @transaction.atomic()
    def update(self, instance, validated_data):
        product_typen = validated_data.pop("product_typen", None)
        hoofd_onderwerp = validated_data.pop(
            "hoofd_onderwerp", "ignore"
        )  # None is a valid value

        if hoofd_onderwerp != "ignore":
            instance_hoofd_onderwerp = instance.get_parent()
            if hoofd_onderwerp is None and instance_hoofd_onderwerp is not None:
                last_root = Onderwerp.get_last_root_node()
                instance.move(last_root, "last-sibling")

            elif hoofd_onderwerp != instance_hoofd_onderwerp:
                instance.move(hoofd_onderwerp, "last-child")

            instance.refresh_from_db()

        instance = super().update(instance, validated_data)
        self._validate_onderwerp(instance)
        self._handle_relations(instance, product_typen)
        instance.save()
        return instance
