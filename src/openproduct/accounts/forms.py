from django.contrib.auth.forms import UserChangeForm as _UserChangeForm

from .models import User
from .utils import validate_max_permissions, validate_max_user_permissions


class PreventPrivilegeEscalationMixin:
    # These class attributes are set by admin._UserAdmin when instantiating the
    # form. Unfortunately, it was not possible to set these via the constructor
    # due to the way Django internals instantiates admin forms.
    _current_user: User | None = None
    _target_user: User | None = None

    def clean(self):
        if self._current_user is None:  # pragma: no cover
            raise RuntimeError("Could not determine current user.")
        if self._target_user is None:  # pragma: no cover
            raise RuntimeError("Could not determine target user.")

        cleaned_data = super().clean()
        user_permissions = cleaned_data.get("user_permissions")
        groups = cleaned_data.get("groups")
        is_superuser = cleaned_data.get("is_superuser")

        # Validate that the permissions that the current user WANTS to give are
        # not more than what the current user has.
        validate_max_permissions(
            self._current_user, user_permissions, groups, is_superuser
        )

        # Validate that the EXISTING permissions of the target user, are not
        # more than your the current user permissions.
        validate_max_user_permissions(self._current_user, self._target_user)

        # Why do we need the above 2 calls?
        #
        # The best example is if a current user has permissions A, and
        # target user has permission A and B. If I try to remove permission B
        # from the target user, the POST-request matches the current users
        # permissions (only A) in the `validate_max_permissions` call. However,
        # when you check the existing permissions with
        # `validate_max_user_permissions`, it detects that the target user
        # actually has permission B as well so you cannot change this user
        # (since he has more permissions).


class UserChangeForm(PreventPrivilegeEscalationMixin, _UserChangeForm):
    pass
