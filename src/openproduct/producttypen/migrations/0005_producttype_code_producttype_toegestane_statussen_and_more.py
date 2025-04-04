# Generated by Django 4.2.17 on 2025-01-17 15:36

from django.db import migrations, models
import openproduct.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("producttypen", "0004_producttype_contacten_producttype_locaties_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="producttype",
            name="code",
            field=models.CharField(
                help_text="code van het product type.",
                max_length=100,
                unique=True,
                verbose_name="code",
            ),
        ),
        migrations.AddField(
            model_name="producttype",
            name="toegestane_statussen",
            field=openproduct.utils.fields.ChoiceArrayField(
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
        migrations.AlterField(
            model_name="producttype",
            name="aanmaak_datum",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="De datum waarop het object is aangemaakt.",
                verbose_name="aanmaak datum",
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="update_datum",
            field=models.DateTimeField(
                auto_now=True,
                help_text="De datum waarop het object voor het laatst is gewijzigd.",
                verbose_name="update datum",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="aanmaak_datum",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="De datum waarop het object is aangemaakt.",
                verbose_name="aanmaak datum",
            ),
        ),
        migrations.AlterField(
            model_name="thema",
            name="update_datum",
            field=models.DateTimeField(
                auto_now=True,
                help_text="De datum waarop het object voor het laatst is gewijzigd.",
                verbose_name="update datum",
            ),
        ),
    ]
