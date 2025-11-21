from django.db import models
from django.utils.translation import gettext_lazy as _

from openproduct.accounts.models import User

from .producttype import ProductType


class PermissionModes(models.TextChoices):
    read_only = "read_only", _("Read-only")
    read_and_write = "read_and_write", _("Read and write")


class ProductTypePermission(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="producttype_permissions"
    )
    producttype = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name="producttype_permissions"
    )

    mode = models.CharField(
        _("mode"),
        max_length=20,
        choices=PermissionModes.choices,
        help_text=_("Permission mode"),
    )

    class Meta:
        verbose_name = _("ProductType Permission")
        unique_together = (("user", "producttype"),)
