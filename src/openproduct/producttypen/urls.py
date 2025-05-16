from django.conf import settings
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from openproduct.locaties.urls import LocatieRouter
from openproduct.producttypen.viewsets import (
    ActieViewSet,
    BestandViewSet,
    ContentElementViewSet,
    ContentLabelViewSet,
    JsonSchemaViewSet,
    LinkViewSet,
    PrijsViewSet,
    ProductTypeViewSet,
    ThemaViewSet,
)

ProductTypenRouter = DefaultRouter(trailing_slash=False)
ProductTypenRouter.register("producttypen", ProductTypeViewSet)

ProductTypenRouter.register("links", LinkViewSet, basename="link")

ProductTypenRouter.register("prijzen", PrijsViewSet, basename="prijs")

ProductTypenRouter.register("themas", ThemaViewSet, basename="thema")

ProductTypenRouter.register("bestanden", BestandViewSet, basename="bestand")

ProductTypenRouter.register("schemas", JsonSchemaViewSet, basename="schema")

ProductTypenRouter.register("content", ContentElementViewSet, basename="content")
ProductTypenRouter.register("acties", ActieViewSet, basename="actie")

ProductTypenRouter.register(
    "contentlabels", ContentLabelViewSet, basename="contentlabel"
)

description = """
Een API voor Producttypen.

Een Producttype is de definitie van een Product. Hierin wordt alle relevante data opgeslagen zoals informatie over de aanvraag.

Een product is een instantie van een producttype (zie Producttypen API), in een product worden onder andere de gegevens van de eigenaar, de benodigde data voor het product en bijvoorbeeld de status vastgelegd.

Een producttype valt onder één of meerdere thema's. Een thema kan onderdeel zijn van een ander thema via het attribuut 'hoofd_thema'.

Een producttype kan worden gelinkt één of meerdere locaties, organisaties en/of contacten.

Daarnaast kunnen de volgende objecten per producttype worden aangemaakt:
- externe codes
- parameters
- zaaktypen
- verzoektypen
- processen
- content
- prijzen
    - prijsopties
    - prijsregels
- links
- bestanden
- acties

"""

custom_settings = {
    "TITLE": "Producttypen API",
    "VERSION": settings.PRODUCTTYPEN_API_VERSION,
    "DESCRIPTION": description,
    "SERVERS": [
        {"url": f"/producttypen/api/v{settings.PRODUCTTYPEN_API_MAJOR_VERSION}"}
    ],
    "TAGS": [
        {
            "name": "themas",
            "description": """
## Opvragen en bewerken van THEMA'S.

### Opmerkingen
- Een thema kan onderdeel zijn van een ander thema, via `hoofd_thema` kan het hoofd thema worden gedefinieerd.
- Een thema kan niet het hoofd thema van zichzelf zijn.
- Een thema moet gepubliceerd zijn voordat zijn sub thema's kunnen worden gepubliceerd.
- Een thema kan niet ongepubliceerd worden als het gepubliceerde sub thema's heeft.
- Een thema niet worden verwijderd als het sub thema's heeft of als er producttypen zijn die aleen gekoppeld zijn aan dit thema.
""",
        },
        {
            "name": "producttypen",
            "description": """
## Opvragen en bewerken van PRODUCTTYPEN.

### Opmerkingen
- Bij het aanmaken en wijzigen van een producttype kan bij `thema_uuids`, `locatie_uuids`, `organisatie_uuids` & `contact__uuids` een lijst met uuids worden meegegeven.
    - `thema_uuids` moet minimaal 1 uuid bevatten.
    - Bij een PUT request word de bestaande lijst overschreven met de nieuwe lijst.
    - Bij een PATCH request wordt de lijst alleen overschreven als het veld wordt meegegeven.
- Bij het veld `uniforme_product_naam` gaat het om de naam uit de Uniforme productnamenlijst (UPL).
- Bij de velden `verbruiksobject_schema_naam` en `dataobject_schema_naam` gaat het om de naam van een JSONSCHEMA.
- De velden `externe_codes`, `parameters`, `zaaktypen`, `verzoektypen` en `processen` worden samen met het producttype genest aangemaakt of gewijzigd.
    - Deze velden zijn een lijst van objecten.
    - Bij een PUT request word de bestaande lijst overschreven met de nieuwe lijst.
    - Bij een PATCH request wordt de lijst alleen overschreven als het veld wordt meegegeven.
- Om de velden `zaaktypen`, `verzoektypen` en `processen` te gebruiken moet er in de ExterneVerwijzingConfig in de beheer interface de url voor elk object worden gedefinieerd.
Tijdens het aanmaken/wijzigen wordt een uuid meegegeven. In de response zal deze uuid worden gecombineerd met de url uit de ExterneVerwijzingConfig.

#### vertalingen
- De velden `naam` en `samenvatting` zijn meertalig, waarbij Nederlands verplicht is en Engels optioneel is.
- Via de reguliere create & update methodes kunnen alleen de Nederlands teksten worden aangemaakt/gewijzigd.
- Via `producttypen/<uuid>/vertaling/<taal>` kan de engelse variant worden gewijzigd.
- met de `Content-Language` header kan worden aangegeven welke taal de response moet zijn.
    - Mocht een producttype de gevraagde vertaling niet hebben, zal worden teruggevallen op Nederlands.
    - via `taal` in de response is te zien welke taal een bepaald producttype is.

#### actuele prijs
- Via `producttypen/actuele-prijzen` en `producttypen/<uuid>/actuele-prijs` kunnen de huidige prijzen worden opgehaald.

""",
        },
        {
            "name": "content",
            "description": """
Opvragen en bewerken van PRODUCTTYPE CONTENT.

### Opmerkingen
- Contentelementen kunnen meerdere labels hebben om aan te geven waar de content overgaat.
- via `producttypen/<uuid>/content/` kunnen alle contentelementen van een producttype worden opgehaald.
- Contentelementen zijn meertalig, waarbij Nederlands verplicht is en Engels optioneel is.
- Via de reguliere create & update methodes kunnen alleen de Nederlands teksten worden aangemaakt/gewijzigd.
- Via `contentelementen/<uuid>/vertaling/<taal>` kan de engelse variant worden gewijzigd.
- met de `Content-Language` header kan worden aangegeven welke taal de response moet zijn.
    - Mocht een content element de gevraagde vertaling niet hebben, zal worden teruggevallen op Nederlands.
    - via `taal` in de response is te zien welke taal een bepaald contentelement is.
""",
        },
        {
            "name": "contentlabels",
            "description": """
## Opvragen van CONTENTLABELS.

### Opmerkingen
- labels kunnen worden aangemaakt in de beheer interface.
""",
        },
        {
            "name": "prijzen",
            "description": """
## Opvragen en bewerken van PRIJZEN.

### Opmerkingen
- Een prijs kan één of meerdere opties of één of meerdere regels hebben.
- Via `actief_vanaf` kunnen prijswijzigingen van te voren worden aangemaakt.
- Een prijs optie bestaat uit een bedrag en een beschrijving en is bedoeld voor simple opties zoals een normale en een spoed prijs.
- Een prijs regel is voor complexere logica en is een link naar een dmn tabel in een externe applicatie.
- Via de Open Product beheeromgeving kunnen de urls van verschillende dmn applicaties worden toegevoegd als een DMNCONFIG object.
- Bij het aanmaken of wijzigen van een regel refereert `tabel_endpoint` naar de url van een aangemaakte DMNCONFIG, `dmn_tabel_id` is de
identifier van de tabel in de dmn omgeving.
- In de response zijn de velden `tabel_endpoint` en `dmn_tabel_id` samengevoegd tot `url`.

- De velden `prijsopties` en `prijsregels` worden samen met het producttype genest aangemaakt of gewijzigd.
    - Bij een PUT request word de bestaande lijst overschreven met de nieuwe lijst.
    - Bij een PATCH request wordt de lijst alleen overschreven als het veld wordt meegegeven.
    - In een PUT of PATCH kan in een optie of regel object een bestaand id worden meegegeven zodat een bestaande optie/regel blijft bestaan.
    Zo kan ook een bestaande optie/regel worden gewijzigd.
    - objecten zonder id zullen worden aangemaakt in een PUT of PATCH.
    - bestaande objecten die niet in de lijst voorkomen met hun id zullen worden verwijderd.
""",
        },
        {
            "name": "schemas",
            "description": """
## Opvragen en bewerken van JSON SCHEMA'S.

### Opmerkingen
- Jsonschema's zijn JSON objecten die worden gebruikt om andere JSON te valideren ([zie jsonschema](https://json-schema.org))
- In Open producten worden jsonschemas gebruikt voor verbruiksobjecten & dataobjecten.
""",
        },
        {"name": "links", "description": "## Opvragen en bewerken van LINKS."},
        {
            "name": "bestanden",
            "description": """
## Opvragen en bewerken van BESTANDEN.

### Opmerkingen
- Om een bestand aan te maken of te wijzigen moet de body van het request `multipart/form-data` zijn.
""",
        },
        {
            "name": "acties",
            "description": """"
## Opvragen en bewerken van ACTIES.

### Opmerkingen
- Een producttype actie is een link naar een dmn tabel uit een externe applicatie.
- Via de Open Product beheeromgeving kunnen de urls van verschillende dmn applicaties worden toegevoegd als een DMNCONFIG object.
- Bij het aanmaken of wijzigen van een actie refereert `tabel_endpoint` naar de url van een aangemaakte DMNCONFIG, `dmn_tabel_id` is de
identifier van de tabel in de dmn omgeving.
- In de response zijn de velden `tabel_endpoint` en `dmn_tabel_id` samengevoegd tot `url`.
""",
        },
        {"name": "locaties", "description": "## Opvragen en bewerken van LOCATIES."},
        {
            "name": "organisaties",
            "description": "## Opvragen en bewerken van ORGANISATIES.",
        },
        {"name": "contacten", "description": "## Opvragen en bewerken van CONTACTEN."},
    ],
}

urlpatterns = [
    # API documentation
    path(
        "openapi.yaml",
        SpectacularAPIView.as_view(
            urlconf="openproduct.producttypen.urls",
            custom_settings=custom_settings,
        ),
        name="schema-producttypen-yaml",
    ),
    path(
        "openapi.json",
        SpectacularJSONAPIView.as_view(
            urlconf="openproduct.producttypen.urls",
            custom_settings=custom_settings,
        ),
        name="schema-producttypen-json",
    ),
    path(
        "schema/",
        SpectacularRedocView.as_view(
            url_name="schema-producttypen-yaml", title=custom_settings["TITLE"]
        ),
        name="schema-redoc-producttypen",
    ),
    path(
        "schema-swagger",
        SpectacularSwaggerView.as_view(url_name="schema-producttypen", title="schema"),
    ),
    path("", include(ProductTypenRouter.urls)),
    path("", include(LocatieRouter.urls)),
]
