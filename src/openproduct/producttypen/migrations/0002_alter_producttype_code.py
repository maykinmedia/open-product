# Generated by Django 4.2.20 on 2025-05-21 09:04

from django.db import migrations, models
import openproduct.producttypen.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ("producttypen", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producttype",
            name="code",
            field=models.CharField(
                help_text="code van het producttype.",
                max_length=255,
                unique=True,
                validators=[
                    openproduct.producttypen.models.validators.validate_producttype_code
                ],
                verbose_name="code",
            ),
        ),
    ]
