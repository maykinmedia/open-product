from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": forms.CheckboxSelectMultiple,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)
