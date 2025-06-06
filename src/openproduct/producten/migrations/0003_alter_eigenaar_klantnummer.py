# Generated by Django 5.2.1 on 2025-06-03 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0002_product_naam"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eigenaar",
            name="klantnummer",
            field=models.CharField(
                blank=True,
                help_text="generiek veld voor de identificatie van een klant of partij.",
                max_length=50,
                verbose_name="Klantnummer",
            ),
        ),
    ]
