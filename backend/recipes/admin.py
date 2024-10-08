from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)

User = get_user_model()


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
    list_display = ("id", "name", "author", "cooking_time", "pub_at")
    search_fields = ("name", "author")
    list_filter = ("tags",)
    empty_value_display = "-пусто-"

    def favorite_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    favorite_count.short_description = "Количество добавлений в избранное"


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
    list_filter = ("user", "recipe")
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
