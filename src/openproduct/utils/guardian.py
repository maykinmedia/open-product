from guardian.admin import GuardedModelAdminMixin as _GuardedModelAdminMixin


class ObjectPermissionMixin:
    def _has_obj_permission(self, request, action, obj=None):
        opts = self.model._meta
        codename = f"{action}_{opts.model_name}"
        perm = f"{opts.app_label}.{codename}"

        if obj is None:
            # For global permissions when obj is None
            return request.user.has_perm(perm)
        else:
            # For object-level permissions
            return request.user.has_perm(perm) and request.user.has_perm(perm, obj)

    def has_change_permission(self, request, obj=None):
        return self._has_obj_permission(request, "change", obj)

    def has_delete_permission(self, request, obj=None):
        return self._has_obj_permission(request, "delete", obj)


class GuardedModelAdminMixin(_GuardedModelAdminMixin, ObjectPermissionMixin):
    pass
