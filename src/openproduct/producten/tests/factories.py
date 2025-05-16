import factory

from ...producttypen.tests.factories import (
    ExterneVerwijzingConfigFactory,
    ProductTypeFactory,
)
from ..models import Document, Eigenaar, Product
from ..models.product import PrijsFrequentieChoices


class ProductFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    prijs = factory.fuzzy.FuzzyDecimal(1, 10)
    frequentie = factory.fuzzy.FuzzyChoice(
        [x[0] for x in PrijsFrequentieChoices.choices]
    )

    class Meta:
        model = Product


class EigenaarFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Eigenaar


class DocumentFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    uuid = factory.Faker("uuid4")
    documenten_api = factory.SubFactory(ExterneVerwijzingConfigFactory)

    class Meta:
        model = Document
