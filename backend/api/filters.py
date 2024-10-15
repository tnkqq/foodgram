from django.db.models import Q
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """filter ingredient by input string."""

    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    """filter recipes by author, tags, favorites, shopping_carts fields."""

    tags = filters.CharFilter(field_name="tags__slug", method="filter_tags")
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "is_favorited", "author", "is_in_shopping_cart")

    def filter_tags(self, queryset, name, value):
        tag_slugs = self.request.query_params.getlist("tags")
        if tag_slugs:
            query = Q(tags__slug=tag_slugs[0])
            for slug in tag_slugs[1:]:
                query |= Q(tags__slug=slug)
            return queryset.filter(query).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        is_favorited_list = self.request.query_params.getlist("is_favorited")

        if is_favorited_list and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        shopping_cart_list = self.request.query_params.getlist(
            "is_in_shopping_cart"
        )
        if shopping_cart_list and user.is_authenticated:
            return queryset.filter(cart__user=user)
        return queryset
