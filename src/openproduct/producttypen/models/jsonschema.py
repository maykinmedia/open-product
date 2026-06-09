from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion
import structlog
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for

from openproduct.utils.jsonschema_validators import validate_jsonschema

logger = structlog.stdlib.get_logger(__name__)


@reversion.register()
class JsonSchema(models.Model):
    naam = models.CharField(
        _("naam"), help_text=_("Naam van het json schema."), max_length=200, unique=True
    )

    schema = models.JSONField(
        _("schema"), help_text=_("Het schema waartegen gevalideerd kan worden.")
    )

    class Meta:
        verbose_name = _("Json schema")
        verbose_name_plural = _("Json Schemas")
        ordering = ("-id",)

    def __str__(self):
        return self.naam

    def clean(self) -> None:
        schema_validator = validator_for(self.schema)
        try:
            schema_validator.check_schema(self.schema)
        except SchemaError as exc:
            raise ValidationError(exc.message)

    def validate(self, json: dict) -> None:
        validate_jsonschema(json, self.schema)
