from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import SpectacularRedocView
from notifications_api_common.utils import notification_documentation
from rest_framework.routers import DefaultRouter

from openproduct.producten.kanalen import KANAAL_PRODUCTEN
from openproduct.producten.viewsets import ProductViewSet
from openproduct.utils.spectacular import SpectacularJSONAPIView, SpectacularYAMLAPIView

ProductRouter = DefaultRouter(trailing_slash=False)
ProductRouter.register("producten", ProductViewSet, basename="product")

description = f"""
Een API voor Producten.

De Producten API heeft 1 endpoint `producten`. Hiermee kunnen producten zelf, de bijbehorende eigenaren en documenten/zaken/taken worden aangemaakt.

## Uitleg per resource

### Product
Een product is een instantie van een producttype (zie producttypen API), in een product worden onder andere de gegevens van de eigenaar, de benodigde data voor het product en bijvoorbeeld de status vastgelegd.
Specifieke product data kan worden opgeslagen in de JSON velden `dataobject` en `verbruiksobject`. Deze velden worden gevalideerd door de `verbruiksobject_schema` & `dataobject_schema` velden van het producttype ([zie jsonschema](https://json-schema.org)).
De status van een product kan alleen worden veranderd naar de een van de `toegestane statussen` gedefineerd op het producttype.

### Eigenaar
Aan een product kunnen één of meerdere eigenaren worden gelinkt. Een eigenaar kan een Klant/Partij (Klantinteracties API), natuurlijk of niet natuurlijke persoon zijn.

### Document, Zaak, Taak
Een document is een verwijzing naar een `EnkelvoudigInformatieObject` uit de [documenten API](https://vng-realisatie.github.io/gemma-zaken/standaard/documenten/).
Een zaak is een verwijziing naar een `Zaak` uit de [zaken API](https://vng-realisatie.github.io/gemma-zaken/standaard/zaken/).
Taken is een verwijzingen naar taken uit externe API's.

---
*Zie de opmerkingen bij de endpoints voor verdere toelichting op specifieke velden.*

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
- `verbruiksobject` & `dataobject` zijn JSON velden en worden gevalideerd vanuit `verbruiksobject_schema` & `dataobject_schema` van het producttype.
- De velden `documenten`, `zaken` en `taken` wordt samen met het product genest aangemaakt of gewijzigd. # TODO
    - dit veld is een lijst van objecten.
    - Bij een PUT request word de bestaande lijst overschreven met de nieuwe lijst.
    - Bij een PATCH request wordt de lijst alleen overschreven als `documenten` wordt meegegeven.
    - Om het veld te gebruiken moet er in de ExterneVerwijzingConfig in de beheer interface de url voor elk object worden gedefinieerd.
    Tijdens het aanmaken/wijzigen wordt een uuid meegegeven. In de response zal deze uuid worden gecombineerd met de url uit de ExterneVerwijzingConfig.

- Het veld `eigenaren` wordt samen met het product genest aangemaakt of gewijzigd maar heeft een paar verschillen met de hiervoor beschreven velden.
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
        "openapi.yaml",
        SpectacularYAMLAPIView.as_view(
            urlconf="openproduct.producten.urls",
            custom_settings=custom_settings,
        ),
        name="schema-producten-yaml",
    ),
    path(
        "openapi.json",
        SpectacularJSONAPIView.as_view(
            urlconf="openproduct.producten.urls",
            custom_settings=custom_settings,
        ),
        name="schema-producten-json",
    ),
    path(
        "schema/",
        SpectacularRedocView.as_view(
            url_name="schema-producten-yaml", title=custom_settings["TITLE"]
        ),
        name="schema-redoc-producten",
    ),
    # actual API
    path("", include(ProductRouter.urls)),
]
