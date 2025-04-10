from django import forms
from django.db import models

import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet as _FilterSet

from openproduct.utils.enums import Operators
from openproduct.utils.helpers import string_to_value


class FilterSet(_FilterSet):
    """
    Add help texts for model field filters
    """

    @classmethod
    def filter_for_field(cls, field, field_name, lookup_expr=None):
        filter = super().filter_for_field(field, field_name, lookup_expr)

        if not filter.extra.get("help_text"):
            filter.extra["help_text"] = getattr(field, "help_text", None)
        return filter


class FilterBackend(DjangoFilterBackend):
    filterset_base = FilterSet


class CharArrayFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ChoiceArrayFilter(django_filters.BaseInFilter, django_filters.ChoiceFilter):
    pass


class UUIDFInFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    pass


class ManyWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        if name not in data:
            return []

        return data.getlist(name)


class ManyCharField(forms.CharField):
    widget = ManyWidget

    def to_python(self, value):
        if not value:
            return []

        return value


class ManyCharFilter(django_filters.CharFilter):
    # django-filter doesn't support several uses of the same query param out of the box
    # so we need to do it ourselves
    field_class = ManyCharField


class TranslationFilter(django_filters.CharFilter):
    """

    Simplifies Django-parler field translations.

    ProductType.naam -> translations__naam
    Product.producttype.naam -> producttype__translations__naam
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "__" in self.field_name:
            field_names = self.field_name.split("__")
            assert len(field_names) == 2

            self.model_field_name = field_names[0]
            self.field_name = field_names[1]

        else:
            self.model_field_name = None

    def filter(self, qs, value):

        if value in django_filters.constants.EMPTY_VALUES:
            return qs

        lookup = "translations__%s__%s" % (self.field_name, self.lookup_expr)
        language_lookup = "translations__language_code"

        if self.model_field_name:
            lookup = f"{self.model_field_name}__{lookup}"
            language_lookup = f"{self.model_field_name}__{language_lookup}"

        language_code = self.parent.request.LANGUAGE_CODE

        qs = self.get_method(qs)(**{lookup: value, language_lookup: language_code})
        return qs


class TranslationInFilter(django_filters.BaseInFilter, TranslationFilter):
    pass


def filter_data_attr_value_part(
    value_part: str, field_name: str, queryset: models.QuerySet
) -> models.QuerySet:
    """
    filter one value part for data_attr filters
    """
    variable, operator, str_value = value_part.rsplit("__", 2)
    real_value = string_to_value(str_value)

    match operator:
        case Operators.EXACT.value:
            #  for exact operator try to filter on string and numeric values
            in_vals = [str_value]
            if real_value != str_value:
                in_vals.append(real_value)
            queryset = queryset.filter(**{f"{field_name}__{variable}__in": in_vals})
        case Operators.ICONTAINS.value:
            # icontains treats everything like strings
            queryset = queryset.filter(
                **{f"{field_name}__{variable}__icontains": str_value}
            )
        case Operators.IN_LIST.value:
            # in must be a list
            values = str_value.split("|")
            queryset = queryset.filter(
                **{
                    f"{field_name}__{variable}__in": [
                        string_to_value(value) for value in values
                    ]
                }
            )

        case _:
            # gt, gte, lt, lte operators
            queryset = queryset.filter(
                **{f"{field_name}__{variable}__{operator}": real_value}
            )
    return queryset
