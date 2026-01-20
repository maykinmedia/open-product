from vng_api_common.pagination import DynamicPageSizePagination


class Pagination(DynamicPageSizePagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500
