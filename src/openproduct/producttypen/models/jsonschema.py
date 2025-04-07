from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import jsonschema  # noqa
import reversion
from jsonschema import validate
from jsonschema.exceptions import (
    SchemaError,
    ValidationError as JsonSchemaValidationError,
)


@reversion.register()
class JsonSchema(models.Model):
    naam = models.CharField(
        _("naam"), help_text=_("Naam van het json schema."), max_length=200, unique=True
    )

    schema = models.JSONField(
        _("schema"), help_text=_("Het schema waartegen gevalideerd kan worden.")
    )

    latest_validator = jsonschema.validators._LATEST_VERSION

    class Meta:
        verbose_name = _("Json schema")
        verbose_name_plural = _("Json Schemas")
        ordering = ("id",)

    def __str__(self):
        return self.naam

    def clean(self):
        try:
            self.latest_validator.check_schema(self.schema)
        except SchemaError as e:
            raise ValidationError(e.message)

    def validate(self, json: dict) -> None:
        try:
            validate(json, self.schema)
        except JsonSchemaValidationError as e:
            raise ValidationError(e.message)
