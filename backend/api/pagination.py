from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response


class PageNumberPaginationDataOnly(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(data)


class UserSubscriptionPagination(PageNumberPagination):
    """custom pagination for user and subs."""

    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


class PageLimitPagination(LimitOffsetPagination):
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_offset(self, request):
        page = request.query_params.get('page', 1)
        limit = self.get_limit(request)
        return (int(page) - 1) * limit
