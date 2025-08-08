import factory.fuzzy
from faker import Faker

from ..models import (
    Actie,
    Bestand,
    ContentElement,
    ContentLabel,
    ExterneCode,
    JsonSchema,
    Link,
    Parameter,
    Prijs,
    PrijsOptie,
    PrijsRegel,
    Proces,
    ProductType,
    Thema,
    UniformeProductNaam,
    VerzoekType,
    ZaakType,
)
from ..models.dmn_config import DmnConfig

fake = Faker()


class UniformeProductNaamFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"upn {n}")
    uri = factory.Sequence(lambda n: f"{fake.url()}/{n}")

    class Meta:
        model = UniformeProductNaam


class ProductTypeFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: f"producttype code {n}")
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


class PrijsFactory(factory.django.DjangoModelFactory):
    actief_vanaf = factory.Faker("date")
    producttype = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = Prijs


class PrijsOptieFactory(factory.django.DjangoModelFactory):
    beschrijving = factory.Faker("sentence")
    bedrag = factory.fuzzy.FuzzyDecimal(1, 10)

    class Meta:
        model = PrijsOptie


class DmnConfigFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"dmn config {n}")
    tabel_endpoint = factory.Sequence(lambda n: f"{fake.url()}/{n}")

    class Meta:
        model = DmnConfig


class PrijsRegelFactory(factory.django.DjangoModelFactory):
    beschrijving = factory.Faker("sentence")
    dmn_config = factory.SubFactory(DmnConfigFactory)
    dmn_tabel_id = factory.Faker("word")

    class Meta:
        model = PrijsRegel


class BestandFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    bestand = factory.django.FileField(filename="test_bestand.txt")

    class Meta:
        model = Bestand


class LinkFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"link {n}")
    url = factory.Faker("url")

    class Meta:
        model = Link


class ContentElementFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)

    class Meta:
        model = ContentElement

    @factory.post_generation
    def content(self, create, extracted, **kwargs):
        self.set_current_language("nl")
        self.content = extracted or fake.word()
        self.save()


class ContentLabelFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"label {n}")

    class Meta:
        model = ContentLabel


class ExterneCodeFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"systeem {n}")
    code = factory.Faker("word")

    class Meta:
        model = ExterneCode


class ParameterFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"parameter {n}")
    waarde = factory.Faker("word")

    class Meta:
        model = Parameter


class ZaakTypeFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    uuid = factory.Faker("uuid4")

    class Meta:
        model = ZaakType


class VerzoekTypeFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    uuid = factory.Faker("uuid4")

    class Meta:
        model = VerzoekType


class ProcesFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    uuid = factory.Faker("uuid4")

    class Meta:
        model = Proces


class JsonSchemaFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"jsonschema {n}")

    class Meta:
        model = JsonSchema


class ActieFactory(factory.django.DjangoModelFactory):
    producttype = factory.SubFactory(ProductTypeFactory)
    naam = factory.Sequence(lambda n: f"actie {n}")
    dmn_config = factory.SubFactory(DmnConfigFactory)
    dmn_tabel_id = factory.Faker("word")

    class Meta:
        model = Actie
