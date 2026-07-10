import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import structlog
import webcolors
from jsonschema import (
    Draft202012Validator,
    FormatError,
    ValidationError as JSONValidationError,
    draft202012_format_checker,
)

from .typing import JSONObject

logger = structlog.stdlib.get_logger(__name__)


@draft202012_format_checker.checks("color")
def is_valid_color(value: object) -> bool:
    """
    Checks if the value is a valid CSS3 color:
        - named CSS3 color
        - hexadecimal color

    Raises FormatError if invalid.
    """
    if not isinstance(value, str):
        raise FormatError(
            _("'{value}' is not a string and therefore not a valid color")
        )

    try:
        webcolors.name_to_hex(value)
    except ValueError:
        try:
            webcolors.hex_to_name(value)
        except ValueError:
            raise FormatError(
                _(
                    "'{value}' is not a valid hexadecimal color and not defined as a named color in CSS3 color".format(
                        value=value
                    )
                )
            )
    return True


@draft202012_format_checker.checks("email")
def is_valid_email(value: object) -> bool:
    """
    Check that 'value' is a reasonably valid email address.

    - Returns False if the value is not a string.
    - Performs a simplified validation.

    """
    pattern = r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
    return bool(re.match(pattern, str(value)))


def validate_jsonschema(
    instance: JSONObject, schema: JSONObject, label: str = "instance"
) -> None:
    """
    Validator for JSONField with appropriate JSON schema.

    Selects the correct validator draft based on the `$schema` keyword
    declared in *schema*, falling back to the latest supported draft.

    Args:
        instance (JSONObject): The JSON object to validate.
        schema (JSONObject): The JSON Schema to validate against.

    Raises:
        ValidationError: Raises a Django ValidationError with the first
            validation message produced by jsonschema.
    """
    try:
        validator = Draft202012Validator(
            schema,
            format_checker=draft202012_format_checker
            if settings.JSONSCHEMA_USE_FORMAT_CHECKER
            else None,
        )
        validator.validate(instance)
    except JSONValidationError as json_error:
        logger.exception("invalid_jsonschema")
        path_list = [str(err) for err in getattr(json_error, "absolute_path", [])]
        if label not in path_list:
            path_list.insert(0, label)
        path = ".".join(path_list)

        raise ValidationError({path: json_error.message})
