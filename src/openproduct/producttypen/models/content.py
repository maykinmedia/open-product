from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion
from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet
from parler.fields import TranslatedField, TranslationsForeignKey
from parler.managers import TranslatableQuerySet
from parler.models import TranslatableModel, TranslatedFieldsModel

from openproduct.utils.models import BaseModel


@reversion.register()
class ContentLabel(BaseModel):
    naam = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = _("Label")
        verbose_name_plural = _("Labels")
        ordering = ("-id",)


class ContentElementQuerySet(TranslatableQuerySet, OrderedModelQuerySet):
    pass


class ContentElementManager(OrderedModelManager.from_queryset(ContentElementQuerySet)):
    pass


@reversion.register(follow=("labels", "producttype", "thema"))
class ContentElement(TranslatableModel, OrderedModel, BaseModel):
    labels = models.ManyToManyField(
        ContentLabel,
        verbose_name=_("labels"),
        blank=True,
        related_name="content_elementen",
        help_text=_("De labels van dit content element"),
    )
    producttype = models.ForeignKey(
        "ProductType",
        verbose_name=_("label"),
        on_delete=models.CASCADE,
        help_text=_("Het producttype van dit content element"),
        related_name="content_elementen",
        null=True,
        blank=True,
    )

    thema = models.ForeignKey(
        "Thema",
        verbose_name=_("thema"),
        on_delete=models.CASCADE,
        related_name="content_elementen",
        null=True,
        blank=True,
        help_text=_("Het thema of subthema van dit content element"),
    )

    content = TranslatedField()

    aanvullende_informatie = TranslatedField()

    order_with_respect_to = "producttype"
    objects = ContentElementManager()

    def __str__(self):
        owner = None
        if self.producttype:
            owner = self.producttype.code
        elif self.thema:
            owner = self.thema.naam
        else:
            owner = _("onbekend")

        labels = ",".join(self.labels.values_list("naam", flat=True))
        return f"{owner} - {labels}"

    class Meta:
        verbose_name = _("content element")
        verbose_name_plural = _("content elementen")
        ordering = ("-id",)

    def clean(self):
        """
        Ensure exactly ONE of (producttype, thema) is provided.
        """
        if self.producttype and self.thema:
            raise ValidationError(
                _("Kies óf een producttype óf een thema, niet beide.")
            )

        if not self.producttype and not self.thema:
            raise ValidationError(_("Geef een producttype of thema op."))

        super().clean()


@reversion.register()
class ContentElementTranslation(TranslatedFieldsModel):
    master = TranslationsForeignKey(
        ContentElement,
        related_name="translations",
        on_delete=models.CASCADE,
        null=True,
    )
    content = models.TextField(
        _("content"),
        help_text=_("De content van dit content element"),
    )
    aanvullende_informatie = models.TextField(
        _("aanvullende informatie"),
        help_text=_("De aanvullende informatie van dit content element"),
        blank=True,
    )

    class Meta:
        unique_together = ("language_code", "master")
        verbose_name = _("Content element vertaling")
        verbose_name_plural = _("Content element vertalingen")
        ordering = ("-id",)
