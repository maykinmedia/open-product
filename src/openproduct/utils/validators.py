from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openproduct.utils.filters import Operators, string_to_value


def validate_charfield_entry(value, allow_apostrophe=False):
    """
    Validates a charfield entry according with Belastingdienst requirements.

    :param value: The input value string to be validated.
    :param allow_apostrophe: Boolean to add the apostrophe character to the
    validation. Apostrophes are allowed in input with ``True`` value. Defaults
    to ``False``.
    :return: The input value if validation passed. Otherwise, raises a
    ``ValidationError`` exception.
    """
    invalid_chars = '/"\\,;' if allow_apostrophe else "/\"\\,;'"

    for char in invalid_chars:
        if char in value:
            raise ValidationError(
                _("The provided value contains an invalid character: %s") % char
            )
    return value


def validate_phone_number(value):
    try:
        int(value.strip().lstrip("0+").replace("-", "").replace(" ", ""))
    except (ValueError, TypeError):
        raise ValidationError(_("Ongeldig telefoonnummer."))

    return value


class CustomRegexValidator(RegexValidator):
    """
    CustomRegexValidator because the validated value is append to the message.
    """

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(force_str(value)):
            message = "{0}: {1}".format(self.message, force_str(value))
            raise ValidationError(message, code=self.code)


validate_postal_code = CustomRegexValidator(
    regex="^[1-9][0-9]{3}\s?[A-Z]{2}$",
    message=_(
        "Invalid postal code. A postal code must consist of 4 numbers followed by two capital letters (e.g. 1234 AB)."
    ),
)


def validate_data_attr_value_part(value_part: str, code: str):
    try:
        variable, operator, val = value_part.rsplit("__", 2)
    except ValueError:
        message = _(
            "Filter '%(value_part)s' heeft niet de format 'key__operator__waarde'"
        ) % {"value_part": value_part}
        raise serializers.ValidationError(message, code=code)

    if operator not in Operators.values:
        message = _("operator `%(operator)s` is niet bekend/ondersteund") % {
            "operator": operator
        }
        raise serializers.ValidationError(message, code=code)

    if operator not in (
        Operators.EXACT,
        Operators.ICONTAINS,
        Operators.IN_LIST,
    ) and isinstance(string_to_value(val), str):
        message = _(
            "Operator `%(operator)s` ondersteunt alleen datums en/of numerieke waarden"
        ) % {"operator": operator}
        raise serializers.ValidationError(message, code=code)


def validate_data_attr(value: list):
    code = "invalid-data-attr-query"

    for value_part in value:
        # check that comma can be only in the value part
        if "," in value_part.rsplit("__", 1)[0]:
            message = _(
                "Filter '%(value_part)s' moet de format 'key__operator__value' hebben, "
                "komma's kunnen alleen in de `waarde` worden toegevoegd"
            ) % {"value_part": value_part}
            raise serializers.ValidationError(message, code=code)

        validate_data_attr_value_part(value_part, code)


class ManyRegexValidator(RegexValidator):
    def __call__(self, values):
        for value in values:
            super().__call__(value)
