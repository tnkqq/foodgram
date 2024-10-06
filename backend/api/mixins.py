from rest_framework import viewsets

from .pagination import PageNumberPaginationDataOnly


class DefaultIngredientTagMixin(viewsets.ReadOnlyModelViewSet):
    """add same pagination for ingredient and tags."""

    pagination_class = PageNumberPaginationDataOnly
