from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils.translation import gettext_lazy as _

class Pagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(
            {
                _("aantal"): self.page.paginator.count,
                _("volgende"): self.get_next_link(),
                _("vorige"): self.get_previous_link(),
                _("resultaten"): data,
            }
        )
