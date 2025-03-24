.. _manual_general:

====================
Algemene onderwerpen
====================

De algemene onderwerpen beschrijven acties voor medewerkers met toegang tot de
beheerinterface van Open Producten (hierna *de admin* genoemd).

In deze handleiding nemen we aan dat Open Producten geïnstalleerd is en beschikbaar
op het adres https://open-producten.gemeente.nl.

.. _manual_login:

Inloggen
========

Om in te loggen in de admin kan je navigeren naar de startpagina
https://open-producten.gemeente.nl. Klik vervolgens op **Beheer**:

.. image:: assets/startpagina.png
    :width: 100%
    :alt: Startpagina

Vul je gebruikersnaam en wachtwoord in op het loginscherm:

.. image:: assets/login.png
    :width: 530
    :align: center
    :alt: Login

Na het aanmelden zie je het dashboard.

Wachtwoord wijzigen
===================

Eenmaal :ref:`ingelogd <manual_login>`, kan je je wachtwoord wijzigen via de
link rechtsboven:

.. image:: assets/change_password_link.png
    :width: 100%
    :alt: Change password link

Vul vervolgens je **huidige** wachtwoord in, je **nieuwe** wachtwoord en
je nieuwe wachtwoord ter **bevestiging**.

Klik rechtsonderin op **Mijn wachtwoord wijzigen** om je nieuwe wachtwoord in
te stellen.

.. note::
    Merk op dat er bepaalde regels gelden om een voldoende sterk
    wachtwoord in te stellen. We raden aan om een *password manager* te
    gebruiken om een voldoende sterk wachtwoord in te stellen.

Dashboard
=========

De gegevens die in de admin beheerd kunnen worden, zijn gegroepeerd op het
dashboard. Deze groepen worden hier verder beschreven. Merk
op dat het mogelijk is dat je bepaalde groepen niet ziet omdat je onvoldoende
rechten hebt.

Accounts
--------

**Gebruikers** zijn de personen die in kunnen loggen in de admin. Aan
gebruikers worden rechten toegekend die bepalen wat ze precies kunnen inzien
en/of beheren. Gebruikers kunnen gedeactiveerd worden, waardoor ze niet langer
in kunnen loggen. Ga naar :ref:`manual_users_add` om te leren hoe je een
gebruiker toevoegt en configureert.

.. _manual_authorizations:

API Autorisaties
----------------

De *API's Open Producten* zijn niet toegankelijk zonder autorisatie.
Dit betekent dat elke applicatie die gegevens ophaalt of registreert in Open
Producten hiervoor geautoriseerd moet zijn. Dit kan via tokens of een oidc provider.

* Voor tokens, zie :ref:`manual_generate_token`.
* Voor het gebruik van een oidc provider zie :ref:`manual_use_oidc`.

Producten
---------

De groep *Producten* laat je toe om gegevens in te kijken die via de Open Producten
API's aangemaakt en/of gewijzigd worden.

**Producten** bevat alle informatie die de *Producten API* ontsluit. Hier kan je
alle aangemaakte **Producten** inzien.

.. _manual_configuration:

Config
------

Het configuratiegedeelte dient om de Open Producten-installatie te configureren.
Typisch wordt dit initieel bij installatie geconfigureerd.

Via **Applicatiegroepen** kan je een **Applicatiegroep** aanmaken. Met deze
**Applicatiegroepen** kunnen de verschillende admin paginas gekoppeld worden aan
menu groepen.

In de **Notificatiescomponentconfiguratie** kan je instellen van welke
*Notificaties API* je gebruik maakt. Je moet een geldige configuratie instellen,
anders worden er door Open Producten geen notificaties verstuurd.

Logs
----

Via **Access attempts** en **Access logs** kan je de inlogpogingen en sessies
in de admin van gebruikers bekijken. Deze worden gelogd om *brute-forcing*
tegen te kunnen gaan en inzicht te verschaffen in wie op welk moment toegang
had tot het systeem.

**Failed notifications** toont de notificaties die Open Zaak probeerde te
versturen, maar om één of andere reden niet slaagden. Je kan hier manueel
notificaties opnieuw versturen of verder onderzoeken waarom de notificatie niet
kon verstuurd worden.

Er worden vaak informatieve logberichten weggeschreven die kunnen wijzen op een
probleem in de Open Producten applicatie. Deze worden via de logs inzichtelijk
gemaakt.

Misc
----

**Websites** bevat gegevens over waar Open Producten gehost wordt. Zorg ervoor dat
de standaard website het juiste domein ingesteld heeft (en dus niet
``example.com``).

**Webauthn devices** is de pagina waar Webauthn apparaten geconfigureerd kunnen
worden.


Lijst- en detailweergaves
=========================

De structuur van de admin volgt voor het grootste deel hetzelfde patroon:

1. Vertrek vanaf het dashboard
2. Klik een onderwerp aan binnen een groep, bijvoorbeeld *Producten*
3. Vervolgens zie je een lijst van gegevens
4. Na het doorklikken op één item op de lijst zie je een detailweergave

We gaan nu dieper in op wat je kan in lijst- en detailweergaves.

.. _manual_general_list:

Lijstweergave
-------------

Als voorbeeld zie je de lijstweergave van *Producten*:

.. image:: assets/product_list.png
    :width: 100%
    :alt: Productenlijst

1. De meeste lijstweergaves hebben een zoekveld waarmee je de lijst van
   gegevens kan doorzoeken. Vaak zoeken deze op identificatie, UUID of een
   ander karakteristiek attribuut.

2. Aan de rechterzijde is er meestal een set aan filters beschikbaar. Deze
   laten je toe om snel de resultaatset te reduceren. Filters kunnen
   gecombineerd worden (combinaties werken als EN-filter).

3. Kolommen zijn sorteerbaar - klik op het kolomhoofd om oplopend te sorteren.
   Klik een tweede keer om aflopend te sorteren. Je kan sorteren op meerdere
   kolommen - er verschijnt dan een nummer die aangeeft op welke kolommen er
   in welke volgorde gesorteerd wordt.

4. In de lijstweergave zijn *bulk acties* beschikbaar. Selecteer de objecten
   waarop je de bulk actie wil toepassen door het vinkje links aan te vinken.
   Kies vervolgens in de dropdown te actie die je uit wil voeren.

   .. warning:: Merk op dat het verwijderen van objecten deze objecten ook echt
      **permanent** verwijdert! Het is zelden nodig om objecten te verwijderen.

5. Typisch is de eerste kolom in een lijstweergave een klikbare link. Door deze
   aan te klikken ga je naar de :ref:`manual_general_detailview` van dat object.

6. Rechtsboven heb je typisch een knop om nieuwe objecten toe te voegen. Deze
   opent een formulier om de objectgegevens in te vullen.

.. _manual_general_detailview:

Detailweergave
--------------

In de detailweergave zie je de gegevens/attributen van één enkel object, al
dan niet aangevuld met de gerelateerde objecten.

Als voorbeeld zie je (een deel van) de detailweergave van een product:

.. image:: assets/product_detail.png
    :width: 100%
    :alt: Product detail

1. De attributen van het product worden opgelijst als bewerkbare velden. Sommige
   attributen zullen niet bewerkbaar zijn, en als je geen bewerkrechten hebt
   zie je alles als alleen-lezen. Verplichte velden worden in het vet gedrukt,
   terwijl optionele velden normaal gedrukt zijn. Indien beschikbaar, dan wordt
   onder het veld een extra helptekst getoond die meer context geeft over de
   betekenis van een veld.

2. Gerelateerde objecten kunnen via de kleine iconen naast het invoer veld
   ingesteld worden.

3. Gerelateerde objecten worden *inline* getoond indien de beheeromgeving
   op deze manier geconfigureerd is.

4. Je kan de geschiedenis inkijken van een specifiek object. Dit toont de
   wijzigingen aangebracht via de admin interface en door wie *en* de audit log
   van wijzigingen die via de API gebeurd zijn.

Wanneer je helemaal naar beneden scrollt (en de juiste rechten hebt), dan zie
je links onderin ook een knop **Verwijderen**. Hierop klikken brengt je naar
een bevestigingsscherm. In dit scherm worden alle gerelateerde objecten
getoond die mee zullen verwijderd worden.

.. warning:: Verwijderen van objecten is permanent! Eenmaal je de verwijdering
   bevestigt kan dit **niet** meer teruggedraaid worden.
