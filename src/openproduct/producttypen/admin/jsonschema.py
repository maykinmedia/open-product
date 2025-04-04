import json

from django import forms
from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin
from openproduct.producttypen.models import JsonSchema


class IndentedJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, **kwargs)


class JsonSchemaAdminForm(forms.ModelForm):
    schema = forms.JSONField(encoder=IndentedJSONEncoder)

    class Meta:
        model = JsonSchema
        fields = "__all__"


@admin.register(JsonSchema)
class JsonSchemaAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    form = JsonSchemaAdminForm
    search_fields = ["naam"]

    def get_changeform_initial_data(self, request):
        return {
            "schema": {
                "type": "object",
                "title": "productDataExample",
                "description": "Voorbeeld",
                "examples": [{"eigenschap1": "Een value", "eigenschap2": 2}],
                "required": ["eigenschap1"],
                "properties": {
                    "eigenschap1": {
                        "type": "string",
                        "description": "Een verplichte eigenschap",
                    },
                    "eigenschap2": {
                        "type": "integer",
                        "description": "Een optionele eigenschap als integer",
                    },
                    "eigenschap3": {
                        "type": "string",
                        "description": "Een optionele eigenschap",
                    },
                },
                "additionalProperties": False,
            }
        }
