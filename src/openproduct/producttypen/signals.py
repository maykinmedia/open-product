from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProductType


@receiver(post_save, sender=ProductType)
def add_contact_organisaties(sender, instance, **kwargs):
    instance.add_contact_organisaties()
