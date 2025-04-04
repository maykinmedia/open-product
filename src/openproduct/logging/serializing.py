from itertools import chain

from django.db import models


def model_to_dict(instance):
    """
    Modified version of django.forms.model_to_dict.

    * it doesn't skip non-editable fields
    * it serializes related objects to their PK instead of passing model instances
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        value = f.value_from_object(instance)
        match f:
            case models.ManyToManyField():
                value = [obj.pk for obj in value]
            case _:
                pass
        data[f.name] = value

    return data


def serialize_instance(instance: models.Model):
    return model_to_dict(instance)
