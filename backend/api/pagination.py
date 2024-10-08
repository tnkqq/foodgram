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
    page_size = None
    page_size_query_param = 'limit'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        self.page = paginator.page(page_number)

        if self.page.number > paginator.num_pages:
            self.page = paginator.page(paginator.num_pages)

        return list(self.page)
