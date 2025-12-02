from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.core.exceptions import PermissionDenied, ValidationError

from ..producttypen.admin.producttypepermission import ProductTypePermissionInline
from .forms import PreventPrivilegeEscalationMixin, UserChangeForm
from .models import User
from .utils import validate_max_user_permissions


@admin.register(User)
class UserAdmin(_UserAdmin):
    form = UserChangeForm
    inlines = (ProductTypePermissionInline,)

    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super().get_form(request, obj, **kwargs)
        assert issubclass(ModelForm, (PreventPrivilegeEscalationMixin, self.add_form))
        # Set the current and target user on the ModelForm class so they are
        # available in the instantiated form. See the comment in the
        # UserChangeForm for more details.
        ModelForm._current_user = request.user
        ModelForm._target_user = obj
        return ModelForm

    def get_inlines(self, request, obj=None):
        return self.inlines if obj else ()

    def user_change_password(self, request, id, form_url=""):
        user = self.get_object(request, unquote(id))
        try:
            validate_max_user_permissions(request.user, user)
        except ValidationError as exc:
            raise PermissionDenied from exc

        return super().user_change_password(request, id, form_url)
