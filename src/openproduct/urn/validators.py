from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_urn_or_url(urn, url, field=""):
    field += " " if field else ""
    if not urn and not url:
        raise ValidationError(_("een {}url of urn is verplicht").format(field))
