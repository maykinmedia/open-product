from django import http
from django.conf import settings
from django.template import TemplateDoesNotExist, loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME
from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


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


class OrderedModelViewSet(ModelViewSet):
    def get_queryset(self):
        return self.queryset.order_by("id")


class IndexView(TemplateView):
    template_name = "index.html"
    # custom context
    component = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"component": self.component})
        return context


class TranslatableViewSetMixin:

    _supported_languages = {
        language["code"]
        for site in settings.PARLER_LANGUAGES
        if isinstance(site, int)
        for language in settings.PARLER_LANGUAGES[site]
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
