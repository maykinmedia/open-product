from django import http
from django.conf import settings
from django.template import TemplateDoesNotExist, loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME

import structlog
from open_api_framework.conf.utils import config
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = structlog.stdlib.get_logger(__name__)

DEFAULT_CODE = "invalid"
DEFAULT_DETAIL = _("Invalid input.")


@requires_csrf_token
def server_error(request, template_name=ERROR_500_TEMPLATE_NAME):
    """
    500 error handler.

    Templates: :template:`500.html`
    Context: None
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        if template_name != ERROR_500_TEMPLATE_NAME:
            # Reraise if it's a missing custom template.
            raise
        return http.HttpResponseServerError(
            b"<h1>Server Error (500)</h1>", content_type="text/html"
        )
    context = {"request": request}
    return http.HttpResponseServerError(template.render(context))


def exception_handler(exc, context):
    """
    Transform 5xx errors into DSO-compliant shape.
    """
    response = drf_exception_handler(exc, context)
    if not response:
        if config("DEBUG", default=False):
            return None

        data = {
            "code": "error",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": _("A server error has occurred."),
        }
        event = "api.uncaught_exception"

        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
        logger.exception(event, exc_info=exc)

        return response

    # exception logger event
    logger.exception(
        "api.handled_exception",
        title=getattr(exc, "default_detail", DEFAULT_DETAIL).strip("'"),
        code=getattr(exc, "default_code", DEFAULT_CODE),
        status=getattr(response, "status_code", status.HTTP_400_BAD_REQUEST),
        data=getattr(response, "data", {}),
        exc_info=False,
    )

    return response


class TranslatableViewSetMixin:
    _supported_languages = {
        language["code"] for language in settings.PARLER_LANGUAGES[None]
    }

    def update_vertaling(self, request, taal, **kwargs):
        partial = request.method == "PATCH"

        instance = self.get_object()

        taal = taal.lower()

        if taal == "nl":
            raise ParseError(_("nl vertaling kan worden aangepast via het model zelf."))

        if taal not in self._supported_languages:
            raise ParseError(_("{} vertaling wordt niet ondersteunt.").format(taal))

        if partial and not request.data:
            raise ParseError(_("patch request mag niet leeg zijn."))

        instance.set_current_language(taal)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def delete_vertaling(self, request, taal, **kwargs):
        instance = self.get_object()

        if taal.lower() == "nl":
            raise ParseError(_("nl vertaling kan worden aangepast via het model zelf."))

        if not instance.has_translation(taal):
            raise NotFound(_("{} vertaling bestaat niet.").format(taal))

        instance.delete_translation(taal)
        return Response(status=status.HTTP_204_NO_CONTENT)
