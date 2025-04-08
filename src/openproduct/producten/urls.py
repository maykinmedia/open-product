from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from notifications_api_common.utils import notification_documentation
from rest_framework.routers import DefaultRouter

from openproduct.producten.kanalen import KANAAL_PRODUCTEN
from openproduct.producten.viewsets import ProductViewSet

ProductRouter = DefaultRouter()
ProductRouter.register("producten", ProductViewSet, basename="product")

description = f"""
Een API voor Producten.

Een product is een instantie van een producttype (zie producttypen API), in een product worden onder andere de gegevens van de eigenaar, de benodigde data voor het product en bijvoorbeeld de status vastgelegd.

### Notificaties

{notification_documentation(KANAAL_PRODUCTEN)}

"""

custom_settings = {
    "TITLE": "Producten API",
    "VERSION": settings.PRODUCTEN_API_VERSION,
    "DESCRIPTION": description,
    "SERVERS": [{"url": f"/producten/api/v{settings.PRODUCTEN_API_MAJOR_VERSION}"}],
    "TAGS": [
        {
            "name": "producten",
            "description": """
## Opvragen en bewerken van PRODUCTEN.

### Opmerkingen
- Bij het aanmaken van een PRODUCT kunnen één of meerdere eigenaren worden toegevoegd, een eigenaar moet een bsn (en/of klantnummer) of een kvk nummer (met of zonder vestigingsnummer) hebben."
- De status opties van een PRODUCT zijn afhankelijk van de `toegestane_statussen` van het producttype.
- Via `start_datum` & `eind_datum` kan de status van een product automatisch op ACTIEF en VERLOPEN worden gezet.
    - Op het moment dat deze velden worden gezet moeten deze statussen zijn toegestaan op het producttype.
    - De status zal via de start_datum alleen naar ACTIEF veranderen mits de status INITIEEL of GEREED is. Voor de eind_datum zijn dit INTIEEL, GEREED of ACTIEF.
- `verbruiksobject` & `dataobject` zijn JSON velden en worden gevalideerd vanuit `vebruiksobject_schema` & `dataobject_schema` van het producttype.
- Het veld `documenten` wordt samen met het producttype genest aangemaakt of gewijzigd.
    - dit veld is een lijst van objecten.
    - Bij een PUT request word de bestaande lijst overschreven met de nieuwe lijst.
    - Bij een PATCH request wordt de lijst alleen overschreven als `documenten` wordt meegegeven.
    - Om het veld te gebruiken moet er in de ExterneVerwijzingConfig in de beheer interface de url voor elk object worden gedefinieerd.
    Tijdens het aanmaken/wijzigen wordt een uuid meegegeven. In de response zal deze uuid worden gecombineerd met de url uit de ExterneVerwijzingConfig.

- Het veld `eigenaren` wordt samen met het producttype genest aangemaakt of gewijzigd maar heeft een paar verschillen met `documenten`.
    - Bij een PUT request word de bestaande lijst overschreven met de nieuwe lijst.
    - Bij een PATCH request wordt de lijst alleen overschreven als het veld wordt meegegeven.
    - In een PUT of PATCH kan in een eigenaar object een bestaand `uuid` worden meegegeven zodat een bestaande eigenaar blijft bestaan.
    Zo kan ook een bestaande eigenaar worden gewijzigd.
    - eigenaren zonder `uuid` zullen worden aangemaakt in een PUT of PATCH.
    - bestaande eigenaren die niet in de lijst voorkomen met hun id zullen worden verwijderd.
""",
        },
    ],
}


urlpatterns = [
    # API documentation
    path(
        "schema/openapi.yaml",
        SpectacularAPIView.as_view(
            urlconf="openproduct.producten.urls",
            custom_settings=custom_settings,
        ),
        name="schema-producten",
    ),
    path(
        "schema/",
        SpectacularRedocView.as_view(
            url_name="schema-producten", title=custom_settings["TITLE"]
        ),
        name="schema-redoc-producten",
    ),
    # actual API
    path("", include(ProductRouter.urls)),
]
