import factory.fuzzy
from faker import Faker

from ..models import (
    Bestand,
    ContentElement,
    Link,
    Prijs,
    PrijsOptie,
    ProductType,
    Thema,
    UniformeProductNaam,
    Vraag,
)

fake = Faker()


class UniformeProductNaamFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"upn {n}")
    uri = factory.Faker("url")

    class Meta:
        model = UniformeProductNaam


class ProductTypeFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: f"product type code {n}")
    gepubliceerd = True
    uniforme_product_naam = factory.SubFactory(UniformeProductNaamFactory)

    class Meta:
        model = ProductType

    @factory.post_generation
    def naam(self, create, extracted, **kwargs):
        self.set_current_language("nl")
        self.naam = extracted or fake.word()
        self.save()

    @factory.post_generation
    def samenvatting(self, create, extracted, **kwargs):
        self.set_current_language("nl")
        self.samenvatting = extracted or fake.sentence()
        self.save()


class ThemaFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"thema {n}")
    beschrijving = factory.Faker("sentence")
    gepubliceerd = True

    class Meta:
        model = Thema


class VraagFactory(factory.django.DjangoModelFactory):
    vraag = factory.Faker("sentence")
    antwoord = factory.Faker("text")

    class Meta:
        model = Vraag


class PrijsFactory(factory.django.DjangoModelFactory):
    actief_vanaf = factory.Faker("date")
    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Prijs


class PrijsOptieFactory(factory.django.DjangoModelFactory):
    beschrijving = factory.Faker("sentence")
    bedrag = factory.fuzzy.FuzzyDecimal(1, 10)

    class Meta:
        model = PrijsOptie


class BestandFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    bestand = factory.django.FileField(filename="test_bestand.txt")

    class Meta:
        model = Bestand


class LinkFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"link {n}")
    url = factory.Faker("url")

    class Meta:
        model = Link


class ContentElementFactory(factory.django.DjangoModelFactory):
    product_type = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = ContentElement

    @factory.post_generation
    def content(self, create, extracted, **kwargs):
        self.set_current_language("nl")
        self.content = extracted or fake.word()
        self.save()
