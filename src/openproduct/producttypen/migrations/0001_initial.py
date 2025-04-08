# Generated by Django 4.2.17 on 2025-04-08 08:05

import datetime
from decimal import Decimal
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import openproduct.utils.fields
import parler.fields
import parler.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("locaties", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentLabel",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("naam", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Label",
                "verbose_name_plural": "Labels",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="DmnConfig",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "naam",
                    models.CharField(
                        help_text="naam van de dmn instantie.",
                        max_length=255,
                        verbose_name="naam",
                    ),
                ),
                (
                    "tabel_endpoint",
                    models.URLField(
                        help_text="basis endpoint voor de dmn tabellen.",
                        unique=True,
                        verbose_name="url",
                    ),
                ),
            ],
            options={
                "verbose_name": "DMN configuratie",
                "verbose_name_plural": "DMN configuraties",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="ExterneVerwijzingConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "zaaktypen_url",
                    models.URLField(
                        blank=True,
                        help_text="Basis url van Zaaktypen API.",
                        verbose_name="Zaaktypen API url",
                    ),
                ),
                (
                    "processen_url",
                    models.URLField(
                        blank=True,
                        help_text="Basis url van processen.",
                        verbose_name="processen url",
                    ),
                ),
                (
                    "verzoektypen_url",
                    models.URLField(
                        blank=True,
                        help_text="Basis url van verzoektypen.",
                        verbose_name="verzoektypen url",
                    ),
                ),
                (
                    "documenten_url",
                    models.URLField(
                        blank=True,
                        help_text="Basis url van Documenten API.",
                        verbose_name="Documenten API url",
                    ),
                ),
            ],
            options={
                "verbose_name": "Externe verwijzingen configuratie",
            },
        ),
        migrations.CreateModel(
            name="JsonSchema",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "naam",
                    models.CharField(
                        help_text="Naam van het json schema.",
                        max_length=200,
                        unique=True,
                        verbose_name="naam",
                    ),
                ),
                (
                    "schema",
                    models.JSONField(
                        help_text="Het schema waartegen gevalideerd kan worden.",
                        verbose_name="schema",
                    ),
                ),
            ],
            options={
                "verbose_name": "Json schema",
                "verbose_name_plural": "Json Schemas",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Prijs",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "actief_vanaf",
                    models.DateField(
                        help_text="De datum vanaf wanneer de prijs actief is.",
                        validators=[
                            django.core.validators.MinValueValidator(
                                datetime.date.today
                            )
                        ],
                        verbose_name="start datum",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prijs",
                "verbose_name_plural": "Prijzen",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="UniformeProductNaam",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "naam",
                    models.CharField(
                        help_text="Uniforme product naam",
                        max_length=255,
                        unique=True,
                        verbose_name="naam",
                    ),
                ),
                (
                    "uri",
                    models.URLField(
                        help_text="Uri naar de UPN definitie.",
                        unique=True,
                        verbose_name="Uri",
                    ),
                ),
                (
                    "is_verwijderd",
                    models.BooleanField(
                        default=False,
                        help_text="Geeft aan of de UPN is verwijderd.",
                        verbose_name="is verwijderd",
                    ),
                ),
            ],
            options={
                "verbose_name": "Uniforme product naam",
                "verbose_name_plural": "Uniforme product namen",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Thema",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "gepubliceerd",
                    models.BooleanField(
                        default=False,
                        help_text="Geeft aan of het object getoond kan worden.",
                        verbose_name="gepubliceerd",
                    ),
                ),
                (
                    "aanmaak_datum",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="De datum waarop het object is aangemaakt.",
                        verbose_name="aanmaak datum",
                    ),
                ),
                (
                    "update_datum",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="De datum waarop het object voor het laatst is gewijzigd.",
                        verbose_name="update datum",
                    ),
                ),
                (
                    "naam",
                    models.CharField(
                        help_text="Naam van het thema.",
                        max_length=255,
                        verbose_name="naam",
                    ),
                ),
                (
                    "beschrijving",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Beschrijving van het thema, ondersteund markdown format.",
                        verbose_name="beschrijving",
                    ),
                ),
                (
                    "hoofd_thema",
                    models.ForeignKey(
                        blank=True,
                        help_text="Het hoofd thema van het thema.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sub_themas",
                        to="producttypen.thema",
                        verbose_name="hoofd thema",
                    ),
                ),
            ],
            options={
                "verbose_name": "thema",
                "verbose_name_plural": "thema's",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="ProductType",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "gepubliceerd",
                    models.BooleanField(
                        default=False,
                        help_text="Geeft aan of het object getoond kan worden.",
                        verbose_name="gepubliceerd",
                    ),
                ),
                (
                    "aanmaak_datum",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="De datum waarop het object is aangemaakt.",
                        verbose_name="aanmaak datum",
                    ),
                ),
                (
                    "update_datum",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="De datum waarop het object voor het laatst is gewijzigd.",
                        verbose_name="update datum",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        help_text="code van het producttype.",
                        max_length=255,
                        unique=True,
                        verbose_name="code",
                    ),
                ),
                (
                    "toegestane_statussen",
                    openproduct.utils.fields.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("gereed", "Gereed"),
                                ("actief", "Actief"),
                                ("ingetrokken", "Ingetrokken"),
                                ("geweigerd", "Geweigerd"),
                                ("verlopen", "Verlopen"),
                            ]
                        ),
                        blank=True,
                        default=list,
                        help_text="toegestane statussen voor producten van dit type.",
                        size=None,
                        verbose_name="toegestane statussen",
                    ),
                ),
                (
                    "keywords",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=100),
                        blank=True,
                        default=list,
                        help_text="Lijst van keywords waarop kan worden gezocht.",
                        size=None,
                        verbose_name="Keywords",
                    ),
                ),
                (
                    "interne_opmerkingen",
                    models.TextField(
                        blank=True,
                        help_text="Interne opmerkingen over het producttype.",
                        verbose_name="interne opmerkingen",
                    ),
                ),
                (
                    "contacten",
                    models.ManyToManyField(
                        blank=True,
                        help_text="De contacten verantwoordelijk voor het producttype.",
                        related_name="producttypen",
                        to="locaties.contact",
                        verbose_name="contacten",
                    ),
                ),
                (
                    "dataobject_schema",
                    models.ForeignKey(
                        blank=True,
                        help_text="JSON schema om het dataobject van een gerelateerd product te valideren.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="producttypen_dataobject_schemas",
                        to="producttypen.jsonschema",
                        verbose_name="dataobject schema",
                    ),
                ),
                (
                    "locaties",
                    models.ManyToManyField(
                        blank=True,
                        help_text="De locaties waar het product beschikbaar is.",
                        related_name="producttypen",
                        to="locaties.locatie",
                        verbose_name="locaties",
                    ),
                ),
                (
                    "organisaties",
                    models.ManyToManyField(
                        blank=True,
                        help_text="organisaties die dit het product aanbieden.",
                        related_name="producttypen",
                        to="locaties.organisatie",
                        verbose_name="organisaties",
                    ),
                ),
                (
                    "themas",
                    models.ManyToManyField(
                        blank=True,
                        help_text="thema's waaraan het producttype is gelinkt.",
                        related_name="producttypen",
                        to="producttypen.thema",
                        verbose_name="thema's",
                    ),
                ),
                (
                    "uniforme_product_naam",
                    models.ForeignKey(
                        help_text="Uniforme product naam gedefinieerd door de overheid.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="producttypen",
                        to="producttypen.uniformeproductnaam",
                        verbose_name="Uniforme Product naam",
                    ),
                ),
                (
                    "verbruiksobject_schema",
                    models.ForeignKey(
                        blank=True,
                        help_text="JSON schema om het verbruiksobject van een gerelateerd product te valideren.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="producttypen_verbruiksobject_schemas",
                        to="producttypen.jsonschema",
                        verbose_name="verbruiksobject schema",
                    ),
                ),
            ],
            options={
                "verbose_name": "Producttype",
                "verbose_name_plural": "Producttypen",
                "ordering": ("-id",),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PrijsRegel",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "beschrijving",
                    models.CharField(
                        help_text="Korte beschrijving van de prijs regel.",
                        max_length=255,
                        verbose_name="beschrijving",
                    ),
                ),
                (
                    "dmn_tabel_id",
                    models.CharField(
                        help_text="id van de dmn tabel binnen de dmn instantie.",
                        max_length=255,
                        verbose_name="dmn tabel id",
                    ),
                ),
                (
                    "dmn_config",
                    models.ForeignKey(
                        help_text="de dmn engine waar de tabel is gedefinieerd.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prijsregels",
                        to="producttypen.dmnconfig",
                        verbose_name="dmn config",
                    ),
                ),
                (
                    "prijs",
                    models.ForeignKey(
                        help_text="De prijs waarbij deze regel hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prijsregels",
                        to="producttypen.prijs",
                        verbose_name="prijs",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prijs regel",
                "verbose_name_plural": "Prijs regels",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="PrijsOptie",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "bedrag",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Het bedrag van de prijs optie.",
                        max_digits=8,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                        verbose_name="bedrag",
                    ),
                ),
                (
                    "beschrijving",
                    models.CharField(
                        help_text="Korte beschrijving van de optie.",
                        max_length=255,
                        verbose_name="beschrijving",
                    ),
                ),
                (
                    "prijs",
                    models.ForeignKey(
                        help_text="De prijs waarbij deze optie hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prijsopties",
                        to="producttypen.prijs",
                        verbose_name="prijs",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prijs optie",
                "verbose_name_plural": "Prijs opties",
                "ordering": ("-id",),
            },
        ),
        migrations.AddField(
            model_name="prijs",
            name="producttype",
            field=models.ForeignKey(
                help_text="Het producttype waarbij deze prijs hoort.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="prijzen",
                to="producttypen.producttype",
                verbose_name="producttype",
            ),
        ),
        migrations.CreateModel(
            name="Link",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "naam",
                    models.CharField(
                        help_text="Naam van de link.",
                        max_length=255,
                        verbose_name="naam",
                    ),
                ),
                (
                    "url",
                    models.URLField(help_text="Url van de link.", verbose_name="Url"),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij deze link hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="links",
                        to="producttypen.producttype",
                        verbose_name="Producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Producttype link",
                "verbose_name_plural": "Producttype links",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="ContentElement",
            fields=[
                (
                    "order",
                    models.PositiveIntegerField(
                        db_index=True, editable=False, verbose_name="order"
                    ),
                ),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "labels",
                    models.ManyToManyField(
                        blank=True,
                        help_text="De labels van dit content element",
                        related_name="content_elementen",
                        to="producttypen.contentlabel",
                        verbose_name="labels",
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype van dit content element",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="content_elementen",
                        to="producttypen.producttype",
                        verbose_name="label",
                    ),
                ),
            ],
            options={
                "verbose_name": "content element",
                "verbose_name_plural": "content elementen",
                "ordering": ("producttype", "order"),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Bestand",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("bestand", models.FileField(upload_to="", verbose_name="bestand")),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij dit bestand hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bestanden",
                        to="producttypen.producttype",
                        verbose_name="producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Producttype bestand",
                "verbose_name_plural": "Producttype bestanden",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="Actie",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "naam",
                    models.CharField(
                        help_text="naam van de actie.",
                        max_length=255,
                        verbose_name="naam",
                    ),
                ),
                (
                    "dmn_tabel_id",
                    models.CharField(
                        help_text="id van de dmn tabel binnen de dmn instantie.",
                        max_length=255,
                        verbose_name="dmn tabel id",
                    ),
                ),
                (
                    "dmn_config",
                    models.ForeignKey(
                        help_text="de dmn engine waar de tabel is gedefinieerd.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="acties",
                        to="producttypen.dmnconfig",
                        verbose_name="dmn config",
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij deze actie hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="acties",
                        to="producttypen.producttype",
                        verbose_name="Producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "actie",
                "verbose_name_plural": "acties",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="ZaakType",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(
                        help_text="Uuid van het zaaktype.", verbose_name="uuid"
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij dit zaaktype hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="zaaktypen",
                        to="producttypen.producttype",
                        verbose_name="producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "zaaktype",
                "verbose_name_plural": "zaaktypen",
                "ordering": ("-id",),
                "unique_together": {("producttype", "uuid")},
            },
        ),
        migrations.CreateModel(
            name="VerzoekType",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(
                        help_text="Uuid van het verzoektype.", verbose_name="uuid"
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij dit verzoektype hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verzoektypen",
                        to="producttypen.producttype",
                        verbose_name="producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "verzoektype",
                "verbose_name_plural": "verzoektypen",
                "ordering": ("-id",),
                "unique_together": {("producttype", "uuid")},
            },
        ),
        migrations.CreateModel(
            name="ProductTypeTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "naam",
                    models.CharField(
                        help_text="naam van het producttype.",
                        max_length=255,
                        verbose_name="producttype naam",
                    ),
                ),
                (
                    "samenvatting",
                    models.TextField(
                        default="",
                        help_text="Korte samenvatting van het producttype.",
                        verbose_name="samenvatting",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="producttypen.producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Producttype vertaling",
                "verbose_name_plural": "Producttype vertalingen",
                "ordering": ("-id",),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Proces",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(
                        help_text="Uuid van het proces.", verbose_name="uuid"
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij dit proces hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="processen",
                        to="producttypen.producttype",
                        verbose_name="producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Proces",
                "verbose_name_plural": "Processen",
                "ordering": ("-id",),
                "unique_together": {("producttype", "uuid")},
            },
        ),
        migrations.AlterUniqueTogether(
            name="prijs",
            unique_together={("producttype", "actief_vanaf")},
        ),
        migrations.CreateModel(
            name="Parameter",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "naam",
                    models.CharField(
                        help_text="De naam van de parameter.",
                        max_length=255,
                        validators=[
                            django.core.validators.RegexValidator("^[^:\\[\\]]+$")
                        ],
                        verbose_name="naam",
                    ),
                ),
                (
                    "waarde",
                    models.CharField(
                        help_text="De waarde van de parameter.",
                        max_length=255,
                        validators=[
                            django.core.validators.RegexValidator("^[^:\\[\\]]+$")
                        ],
                        verbose_name="waarde",
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij deze parameter hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parameters",
                        to="producttypen.producttype",
                        verbose_name="producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "parameter",
                "verbose_name_plural": "parameters",
                "ordering": ("-id",),
                "unique_together": {("producttype", "naam")},
            },
        ),
        migrations.CreateModel(
            name="ExterneCode",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "naam",
                    models.CharField(
                        help_text="De naam van het systeem van de externe producttype code.",
                        max_length=255,
                        validators=[
                            django.core.validators.RegexValidator("^[^:\\[\\]]+$")
                        ],
                        verbose_name="naam",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        help_text="De code van het producttype in het externe systeem.",
                        max_length=255,
                        validators=[
                            django.core.validators.RegexValidator("^[^:\\[\\]]+$")
                        ],
                        verbose_name="code",
                    ),
                ),
                (
                    "producttype",
                    models.ForeignKey(
                        help_text="Het producttype waarbij deze externe code hoort.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="externe_codes",
                        to="producttypen.producttype",
                        verbose_name="producttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "externe producttype code",
                "verbose_name_plural": "externe producttype codes",
                "ordering": ("-id",),
                "unique_together": {("producttype", "naam")},
            },
        ),
        migrations.CreateModel(
            name="ContentElementTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text="De content van dit content element",
                        verbose_name="content",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="producttypen.contentelement",
                    ),
                ),
            ],
            options={
                "verbose_name": "Content element vertaling",
                "verbose_name_plural": "Content element vertalingen",
                "ordering": ("-id",),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
