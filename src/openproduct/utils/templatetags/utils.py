from typing import Any

from django import template
from django.conf import settings
from django.utils.html import escape, format_html, mark_safe

register = template.Library()


@register.inclusion_tag("utils/includes/version_info.html")
def show_version_info():
    return {
        "RELEASE": settings.RELEASE,
        "GIT_SHA": settings.GIT_SHA,
    }


@register.simple_tag(takes_context=True)
def show_environment_info(context: dict[str, Any]) -> str:
    if not settings.SHOW_ENVIRONMENT:
        return ""
    if (user := context.get("user")) is None or not user.is_authenticated:
        return ""

    style_tokens = {
        "background-color": settings.ENVIRONMENT_BACKGROUND_COLOR,
        "color": settings.ENVIRONMENT_FOREGROUND_COLOR,
    }
    _inline_style_bits = [
        f"--admin-env-info-{key}: {value}".format(key=key, value=escape(value))
        for key, value in style_tokens.items()
    ]
    return format_html(
        """<div class="env-info" style="{style}">{label}</div>""",
        label=settings.ENVIRONMENT_LABEL,
        style=mark_safe("; ".join(_inline_style_bits)),
    )
