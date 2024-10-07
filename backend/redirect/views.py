import short_url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Recipe


def redirect_to_full_link(request, short_code):
    """View для перенаправления короткой ссылки на полный URL рецепта."""
    try:
        recipe_id = short_url.decode_url(short_code)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        full_url = reverse(f"recipes/{recipe.id}/")
        return redirect(full_url)
    except (ValueError, Recipe.DoesNotExist):
        return HttpResponse(
            "Invalid short code or recipe not found",
            status=404)