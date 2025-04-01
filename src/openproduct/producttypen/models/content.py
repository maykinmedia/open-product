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


class ContentElementQuerySet(TranslatableQuerySet, OrderedModelQuerySet):
    pass


class ContentElementManager(OrderedModelManager.from_queryset(ContentElementQuerySet)):
    pass


@reversion.register(follow=("labels", "product_type"))
class ContentElement(TranslatableModel, OrderedModel, BaseModel):
    labels = models.ManyToManyField(
        ContentLabel,
        verbose_name=_("labels"),
        blank=True,
        related_name="content_elementen",
        help_text=_("De labels van dit content element"),
    )
    product_type = models.ForeignKey(
        "ProductType",
        verbose_name=_("label"),
        on_delete=models.CASCADE,
        help_text=_("Het product type van dit content element"),
        related_name="content_elementen",
    )

    content = TranslatedField()

    order_with_respect_to = "product_type"
    objects = ContentElementManager()

    def __str__(self):
        return f"{self.product_type} - {','.join(list(self.labels.values_list('naam', flat=True)))}"

    class Meta:
        verbose_name = _("content element")
        verbose_name_plural = _("content elementen")
        ordering = ("product_type", "order")


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

    class Meta:
        unique_together = ("language_code", "master")
        verbose_name = _("Content element vertaling")
        verbose_name_plural = _("Content element vertalingen")
