# Generated by Django 5.2.3 on 2025-06-17 08:26

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producten', '0004_taak_zaak'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='prijs',
            field=models.DecimalField(decimal_places=2, help_text='De prijs van het product.', max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='prijs'),
        ),
    ]
