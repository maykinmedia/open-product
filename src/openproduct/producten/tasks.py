from django.db import transaction

from openproduct.celery import app
from openproduct.producten.models import Product


def updated_based_on_dates():
    for product in Product.objects.iterator():
        if product.check_start_datum() or product.check_eind_datum():
            product.save()


@app.task
@transaction.atomic()
def set_product_states():
    updated_based_on_dates()
