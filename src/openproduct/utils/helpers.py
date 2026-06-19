from datetime import date, datetime, time, timedelta

from django.db import models
from django.utils.dateparse import parse_duration


def string_to_value(value: str) -> str | float | date | datetime | time | timedelta:
    if not value or not value.strip():
        return value
    if is_number(value):
        return float(value)
    elif is_date(value):
        return date.fromisoformat(value)
    elif is_datetime(value):
        return datetime.fromisoformat(value)
    elif is_time(value):
        return time.fromisoformat(value)
    elif is_duration(value):
        return parse_duration(value)

    return value


def is_datetime(value: str) -> bool:
    try:
        dt = datetime.fromisoformat(value)
        return isinstance(dt, datetime)
    except (ValueError, TypeError):
        return False


def is_time(value: str) -> bool:
    try:
        time.fromisoformat(value)
        return True
    except (ValueError, TypeError):
        return False


def is_duration(value: str) -> bool:
    try:
        return parse_duration(value) is not None
    except (ValueError, TypeError):
        return False


def is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except (ValueError, TypeError):
        return False

    return True


def is_number(value: str) -> bool:
    try:
        float(value)
    except (ValueError, TypeError):
        return False

    return True


def display_choice_values_for_help_text(choices: type[models.TextChoices]) -> str:
    items = []

    for key, value in choices.choices:
        item = f"* `{key}` - {value}"
        items.append(item)

    return "\n".join(items)
