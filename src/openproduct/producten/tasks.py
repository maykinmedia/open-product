from django.db import transaction

from openproduct.celery import app
from openproduct.producten.models import Product


def updated_based_on_dates():
    for product in Product.objects.all():
        product.save()


@app.task
@transaction.atomic()
def set_product_states():
    updated_based_on_dates()
