from itertools import chain

from django.db import models


def model_to_dict(instance):
    """
    Modified version of django.forms.model_to_dict.

    * it doesn't skip non-editable fields
    * it serializes related objects to their PK instead of passing model instances
    * it serializers FileField objects to their filename
    * it serializers ManyToOneRel fields recursively
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        value = f.value_from_object(instance)
        match f:
            case models.ManyToManyField():
                value = [obj.pk for obj in value]
            case models.FileField():
                value = value.name
            case _:
                pass
        data[f.name] = value

    for obj in opts.related_objects:
        manager = getattr(instance, obj.related_name, None)
        data[obj.related_name] = [
            model_to_dict(instance) for instance in manager.iterator()
        ]

    return data


def serialize_instance(instance: models.Model):
    return model_to_dict(instance)
