# Generated by Django 4.2.20 on 2025-05-16 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producten", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="naam",
            field=models.CharField(
                blank=True,
                help_text="De naam van dit product.",
                max_length=255,
                verbose_name="naam",
            ),
        ),
    ]
