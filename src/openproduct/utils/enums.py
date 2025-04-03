from django.db import models
from django.utils.translation import gettext_lazy as _


class Operators(models.TextChoices):
    EXACT = "exact", _("gelijk aan")
    GT = "gt", _("groter dan")
    GTE = "gte", _("groter dan of gelijk aan")
    LT = "lt", _("kleiner dan")
    LTE = "lte", _("kleiner dan of gelijk aan")
    ICONTAINS = "icontains", _("hoofdletterongevoelige gedeeltelijke match")
    IN_LIST = "in", _("in een lijst van waarden gescheiden door `|`")
