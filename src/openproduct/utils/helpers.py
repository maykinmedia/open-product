from datetime import date

from django.db import models


def string_to_value(value: str) -> str | float | date:
    if is_number(value):
        return float(value)
    elif is_date(value):
        return date.fromisoformat(value)

    return value


def is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False

    return True


def is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False

    return True


def display_choice_values_for_help_text(choices: type[models.TextChoices]) -> str:
    items = []

    for key, value in choices.choices:
        item = f"* `{key}` - {value}"
        items.append(item)

    return "\n".join(items)
