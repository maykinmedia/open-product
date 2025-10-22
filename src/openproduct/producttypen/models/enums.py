from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductStateChoices(models.TextChoices):
    INITIEEL = "initieel", _("Initieel")
    IN_AANVRAAG = "in_aanvraag", _("In aanvraag")
    GEREED = "gereed", _("Gereed")
    ACTIEF = "actief", _("Actief")
    INGETROKKEN = "ingetrokken", _("Ingetrokken")
    GEWEIGERD = "geweigerd", _("Geweigerd")
    VERLOPEN = "verlopen", _("Verlopen")


class DoelgroepChoices(models.TextChoices):
    BURGERS = "burgers", _("Burgers")
    INTERNE_ORGANISATIE = "interne_organisatie", _("Interne organisatie")
    SAMENWERKINGSPARTNERS = "samenwerkingspartners", _("Samenwerkingspartners")
    BEDRIJVEN_EN_INSTELLINGEN = (
        "bedrijven_en_instellingen",
        _("Bedrijven en instellingen"),
    )
