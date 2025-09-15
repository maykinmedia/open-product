from django.apps import AppConfig
from django.db import models

from rest_framework.serializers import ModelSerializer

from .fields import JSONObjectField


class UtilsConfig(AppConfig):
    name = "openproduct.utils"

    def ready(self):
        field_mapping = ModelSerializer.serializer_field_mapping
        field_mapping[models.JSONField] = JSONObjectField
