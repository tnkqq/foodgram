from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNumberPaginationDataOnly(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(data)


class UserSubscriptionPagination(PageNumberPagination):
    """custom pagination for user and subs."""

    page_size = 10
    limit_size_query_param = "limit"
    max_page_size = 100


class PageLimitPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'
