from rest_framework.permissions import (
    DjangoModelPermissions as _DjangoModelPermissions,
    DjangoObjectPermissions as _DjangoObjectPermissions,
)


class DjangoModelPermissions(_DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class DjangoObjectPermissions(_DjangoObjectPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class DjangoObjectPermissionsProduct(DjangoObjectPermissions):
    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            return request.user.has_perms(("producttypen.producten",), obj.producttype)

        return False
