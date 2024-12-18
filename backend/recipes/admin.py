from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)

User = get_user_model()


class IngredientsInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(form.cleaned_data for form in self.forms):
            raise ValidationError(
                _("Укажите хотя бы один ингредиент в рецепте")
            )


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    formset = IngredientsInlineFormset
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("slug",)
    list_filter = ("slug",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "cooking_time",
        "pub_at",
        "favorite_count",
    )

    def favorite_count(self, obj):
        """Возвращает количество добавлений в избранное для рецепта."""
        return obj._favorite_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _favorite_count=Count("favorited_by", distinct=True),
        )
        return queryset

    favorite_count.short_description = "Количество добавлений в избранное"

    inlines = (IngredientsInline,)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient")
    search_fields = ("recipe",)
    list_filter = ("ingredient",)
    empty_value_display = "-пусто-"


@admin.register(FavoriteRecipe)
class FavoriteRecipe(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")
    empty_value_display = "-пусто-"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "following")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")
    search_fields = ("emai", "username")
