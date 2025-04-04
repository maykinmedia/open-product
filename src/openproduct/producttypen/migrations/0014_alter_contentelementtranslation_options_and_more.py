# Generated by Django 4.2.17 on 2025-04-01 09:41

from django.db import migrations
import django.db.models.deletion
import parler.fields


class Migration(migrations.Migration):

    dependencies = [
        (
            "producttypen",
            "0013_externeverwijzingconfig_zaaktype_verzoektype_proces",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contentelementtranslation",
            options={
                "verbose_name": "Content element vertaling",
                "verbose_name_plural": "Content element vertalingen",
            },
        ),
        migrations.AlterModelOptions(
            name="producttypetranslation",
            options={
                "verbose_name": "Producttype vertaling",
                "verbose_name_plural": "Producttype vertalingen",
            },
        ),
        migrations.AlterField(
            model_name="contentelementtranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="producttypen.contentelement",
            ),
        ),
        migrations.AlterField(
            model_name="producttypetranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="producttypen.producttype",
            ),
        ),
        migrations.AlterModelTable(
            name="contentelementtranslation",
            table=None,
        ),
        migrations.AlterModelTable(
            name="producttypetranslation",
            table=None,
        ),
    ]
