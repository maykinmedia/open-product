# Generated by Django 5.2.1 on 2025-06-04 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producttypen", "0004_actie_mapping_prijsregel_mapping"),
    ]

    operations = [
        migrations.AddField(
            model_name="externeverwijzingconfig",
            name="taken_url",
            field=models.URLField(
                blank=True,
                help_text="Basis url van Taken API.",
                verbose_name="Taken API url",
            ),
        ),
        migrations.AddField(
            model_name="externeverwijzingconfig",
            name="zaken_url",
            field=models.URLField(
                blank=True,
                help_text="Basis url van Zaken API.",
                verbose_name="Zaken API url",
            ),
        ),
    ]
