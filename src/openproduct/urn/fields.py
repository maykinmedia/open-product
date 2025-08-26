from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

UUID_REGEX = (
    "([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"
)
URN_REGEX = "([a-z-]+):([a-z-]+):([a-z-]+):([a-z-]+)"


class UrnField(models.CharField):
    description = _("URN")
    default_validators = [RegexValidator(f"^{URN_REGEX}:{UUID_REGEX}$")]


class UuidURLValidator(URLValidator):
    def __init__(self, **kwargs):
        super().__init__(schemes=["http", "https"], **kwargs)
        self.uuid_validator = RegexValidator(
            regex=f"^.*/{UUID_REGEX}$", message="URL must end with a UUID."
        )

    def __call__(self, value):
        super().__call__(value)

        self.uuid_validator(value)


class UrlField(models.URLField):
    default_validators = [UuidURLValidator()]


class BaseUrnField(models.CharField):
    default_validators = [RegexValidator(f"^{URN_REGEX}$")]
