import re

from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

UUID_REGEX = (
    "([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"
)


class UuidURLValidator(URLValidator):
    def __init__(self, **kwargs):
        super().__init__(schemes=["http", "https"], **kwargs)
        self.uuid_validator = RegexValidator(
            regex=f"^.*/{UUID_REGEX}$", message="URL must end with a UUID."
        )

    def __call__(self, value):
        super().__call__(value)

        self.uuid_validator(value)


class URNValidator(RegexValidator):
    """
    The basic syntax for a URN is defined using the
    Augmented Backus-Naur Form (ABNF) as specified in [RFC5234].

    URN Syntax:

        namestring    = assigned-name
                        [ rq-components ]
                        [ "#" f-component ]

        assigned-name = "urn" ":" NID ":" NSS

        NID           = (alphanum) 0*30(ldh) (alphanum)
        ldh           = alphanum / "-"
        NSS           = pchar *(pchar / "/")

        rq-components = [ "?+" r-component ]
                        [ "?=" q-component ]
        r-component   = pchar *( pchar / "/" / "?" )
        q-component   = pchar *( pchar / "/" / "?" )

        f-component   = fragment

        ; general URI syntax rules (RFC3986)
        fragment      = *( pchar / "/" / "?" )
        pchar         = unreserved / pct-encoded / sub-delims / ":" / "@"
        pct-encoded   = "%" HEXDIG HEXDIG
        unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
        sub-delims    = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="

        alphanum      = ALPHA / DIGIT  ; obsolete, usage is deprecated

    The question mark character "?" can be used without percent-encoding
    inside r-components, q-components, and f-components.  Other than
    inside those components, a "?" that is not immediately followed by
    "=" or "+" is not defined for URNs and SHOULD be treated as a syntax
    error by URN-specific parsers and other processors.

    https://datatracker.ietf.org/doc/html/rfc8141
    """

    HEXDIG = r"[0-9A-Fa-f]"
    ALPHANUM = r"[A-Za-z0-9]"
    pchar = rf"(?:{ALPHANUM}|[-._~]|%{HEXDIG}{HEXDIG}|[!$&'()*+,;=]|[:@])"

    # assigned-name
    NID = rf"{ALPHANUM}(?:{ALPHANUM}|-){{0,30}}{ALPHANUM}"
    NSS = rf"{pchar}(?:{pchar}|/)*"
    assigned_name = rf"urn:{NID}:{NSS}"

    # optional r/q components
    rq_components = (
        rf"(?:\?\+{pchar}(?:{pchar}|/|\?)*)?(?:\?={pchar}(?:{pchar}|/|\?)*)?"
    )

    # optional f-component
    f_component = rf"{pchar}(?:{pchar}|/|\?)*"

    # complete URN regex (RFC 8141)
    urn_pattern = rf"^{assigned_name}{rq_components}(?:#{f_component})?$"

    message = "Voer een geldige waarde in."
    code = "invalid_urn"

    def __init__(self):
        super().__init__(
            regex=re.compile(self.urn_pattern),
            message=self.message,
            code=self.code,
        )


class UrnField(models.CharField):
    description = _("URN (RFC 8141)")
    default_validators = [URNValidator(), RegexValidator(f":uuid:{UUID_REGEX}$", _("Urn moet eindigen met `:uuid:<uuid>`."))]


class UrlField(models.URLField):
    default_validators = [UuidURLValidator()]


class BaseUrnField(models.CharField):
    default_validators = [
        URNValidator(),
        RegexValidator(
            ":uuid$",
            _(
                "Base urn mag niet eindigen met :uuid, dit is onderdeel van de volledige urn van een object."
            ),
            inverse_match=True,
        ),
        RegexValidator(":$", _("Base urn mag niet eindigen met :"), inverse_match=True),
    ]
