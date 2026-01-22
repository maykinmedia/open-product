from django.contrib import admin

from django_otp.plugins.otp_static.admin import StaticDeviceAdmin
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice

from openproduct.utils.admin import user_model_search_fields_nl

fields, help_text = user_model_search_fields_nl(["username", "email"])


admin.site.unregister(TOTPDevice)


@admin.register(TOTPDevice)
class DutchTOTPDeviceAdmin(TOTPDeviceAdmin):
    search_fields = fields
    search_help_text = help_text


admin.site.unregister(StaticDevice)


@admin.register(StaticDevice)
class DutchStaticDeviceAdmin(StaticDeviceAdmin):
    search_fields = fields
    search_help_text = help_text
