from uuid import uuid4

import factory

from ...producttypen.tests.factories import ProductTypeFactory
from ..models import Document, Eigenaar, Product, Taak, Zaak
from ..models.product import PrijsFrequentieChoices


class ProductFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    prijs = factory.fuzzy.FuzzyDecimal(1, 10)
    frequentie = factory.fuzzy.FuzzyChoice(
        [x[0] for x in PrijsFrequentieChoices.choices]
    )
    aanvraag_zaak_urn = factory.Maybe(
        "aanvraag_zaak_url",
        yes_declaration=None,
        no_declaration=f"urn:nld:maykin:openzaak:ztc:zaak:uuid:{uuid4()}",
    )

    class Meta:
        model = Product


class EigenaarFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Eigenaar


class DocumentFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Document


class ZaakFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Zaak


class TaakFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Taak
