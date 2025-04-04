from typing import Dict, cast

from django.db.models import Field, Model

from glom import glom
from notifications_api_common.kanalen import Kanaal as _Kanaal
from rest_framework.request import Request


class Kanaal(_Kanaal):
    @staticmethod
    def get_field(model: Model, field: str) -> Field:
        """
        Function to retrieve a field from a Model, can also be passed a path to a field
        (e.g. `producttype.id`)
        """
        if "." in field:
            model_field = None
            bits = field.split(".")
            for i, part in enumerate(bits):
                model_field = model._meta.get_field(part)
                if fk_field := getattr(model_field, "fk_field", None):
                    model_field = model._meta.get_field(fk_field)
                if i != len(bits):
                    model = cast(Model, model_field.related_model)
            assert model_field, "Could not find field on model"
            return model_field
        return model._meta.get_field(field)

    def get_kenmerken(
        self, obj: Model, data: dict | None = None, request: Request | None = None
    ) -> Dict:
        """
        Overridden to support sending kenmerken that are not directly part of the main
        resource (e.g `Product.producttype.id`)
        """
        data = data or {}
        kenmerken = {}
        for kenmerk in self.kenmerken:
            value = data.get(kenmerk, glom(obj, kenmerk, default=""))
            kenmerken[kenmerk] = value
        return kenmerken
