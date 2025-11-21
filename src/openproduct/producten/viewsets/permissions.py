from rest_framework.permissions import BasePermission

from openproduct.producttypen.models.producttypepermission import (
    PermissionModes,
    ProductTypePermission,
)


class ProductTypeObjectPermission(BasePermission):
    def user_has_rw_perm_for_producttype_uuid(self, user, producttype_uuid: str):
        return ProductTypePermission.objects.filter(
            user=user,
            producttype__uuid=producttype_uuid,
            mode=PermissionModes.read_and_write,
        ).exists()

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action == "create":
            producttype_uuid = request.data.get("producttype_uuid")
            if not self.user_has_rw_perm_for_producttype_uuid(
                request.user, producttype_uuid
            ):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # check permission for new producttype passed in update
        if new_producttype_id := request.data.get("producttype_uuid"):
            if new_producttype_id != obj.producttype.uuid:
                if not self.user_has_rw_perm_for_producttype_uuid(
                    request.user, new_producttype_id
                ):
                    return False

        obj_producttype_perm = ProductTypePermission.objects.filter(
            user=request.user, producttype=obj.producttype
        ).first()

        if not obj_producttype_perm:
            return False

        if view.action == "retrieve":
            return True

        return obj_producttype_perm.mode == PermissionModes.read_and_write
