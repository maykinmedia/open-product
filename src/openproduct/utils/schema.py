from typing import Optional, Type

from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from rest_framework import serializers, status

from openproduct.utils.serializers import DetailErrorSerializer, ErrorSerializer

ERRORS = {
    status.HTTP_400_BAD_REQUEST: OpenApiResponse(  # TODO: should this be on GET requests?
        response=ErrorSerializer,
        description="Validation error",
        examples=[
            OpenApiExample(
                "Bad request example",
                description="Errors worden per veld teruggegeven. Hieronder volgt een voorbeeld.",
                value={
                    "veld_a": ["Dit veld is vereist."],
                    "veld_b": ["‘<uuid>’ is geen geldige UUID."],
                },
            ),
        ],
    ),
    status.HTTP_403_FORBIDDEN: DetailErrorSerializer,
}


class AutoSchema(_AutoSchema):
    def get_response_serializers(
        self,
    ) -> dict[int, Optional[Type[serializers.Serializer]]]:
        """append error serializers"""
        response_serializers = super().get_response_serializers()

        if self.method == "DELETE":
            status_code = 204
            serializer = None
        elif self._is_create_operation():
            status_code = 201
            serializer = response_serializers
        else:
            status_code = 200
            serializer = response_serializers

        responses = {
            status_code: serializer,
            **ERRORS,
        }
        return responses
