## Notificaties
## Berichtkenmerken voor Open Product API

Kanalen worden typisch per component gedefinieerd. Producers versturen berichten op bepaalde kanalen,
consumers ontvangen deze. Consumers abonneren zich via een notificatiecomponent (
zoals <a href="https://notificaties-api.vng.cloud/api/v1/schema/" rel="nofollow">https://notificaties-api.vng.cloud/api/v1/schema/</a>)
op berichten.

Hieronder staan de kanalen beschreven die door deze component gebruikt worden, met de kenmerken bij elk bericht.

De architectuur van de notificaties staat beschreven
op <a href="https://github.com/VNG-Realisatie/notificaties-api" rel="nofollow">https://github.com/VNG-Realisatie/notificaties-api</a>.

### producten

**Kanaal**
`producten`

**Main resource**

`product`

**Kenmerken**

* `producttype.id`:
* `producttype.uniforme_product_naam`: Uniforme product naam gedefinieerd door de overheid.
* `producttype.code`: code van het producttype.

**Resources en acties**

* <code>product</code>: create, update, destroy


