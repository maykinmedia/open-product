# Generated by Django 4.2.17 on 2025-03-14 13:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import openproduct.producten.models.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0006_product_dataobject"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="bsn",
        ),
        migrations.RemoveField(
            model_name="product",
            name="kvk",
        ),
        migrations.CreateModel(
            name="Eigenaar",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "bsn",
                    models.CharField(
                        blank=True,
                        help_text="Het BSN van de product eigenaar, BSN van 8 karakters moet met een extra 0 beginnen.",
                        validators=[
                            openproduct.producten.models.validators.validate_bsn
                        ],
                        verbose_name="Burgerservicenummer",
                    ),
                ),
                (
                    "kvk_nummer",
                    models.CharField(
                        blank=True,
                        help_text="Het kvk nummer van de product eigenaar",
                        max_length=8,
                        validators=[
                            django.core.validators.MinLengthValidator(8),
                            django.core.validators.RegexValidator("^[0-9]*$"),
                        ],
                        verbose_name="KVK nummer",
                    ),
                ),
                (
                    "vestigingsnummer",
                    models.CharField(
                        blank=True,
                        help_text="Een korte unieke aanduiding van een vestiging.",
                        max_length=24,
                        verbose_name="Vestigingsnummer",
                    ),
                ),
                (
                    "klantnummer",
                    models.CharField(
                        blank=True,
                        help_text="generiek veld voor de identificatie van een klant.",
                        max_length=50,
                        verbose_name="Klantnummer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        help_text="De organisatie van het contact",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eigenaren",
                        to="producten.product",
                        verbose_name="product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Eigenaar",
                "verbose_name_plural": "Eigenaren",
            },
        ),
    ]
