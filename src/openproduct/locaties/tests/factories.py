import factory

from ..models import Contact, Locatie, Organisatie


class OrganisatieFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"organisatie {n}")
    code = factory.Sequence(lambda n: f"organisatie code {n}")
    straat = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")
    stad = factory.Faker("city", locale="nl_NL")

    class Meta:
        model = Organisatie


class LocatieFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"locatie {n}")
    straat = factory.Faker("street_name", locale="nl_NL")
    postcode = factory.Faker("postcode", locale="nl_NL")
    email = factory.Faker("email")

    class Meta:
        model = Locatie


class ContactFactory(factory.django.DjangoModelFactory):
    organisatie = factory.SubFactory(OrganisatieFactory)
    naam = factory.Faker("name")
    rol = factory.Faker("word")

    class Meta:
        model = Contact
