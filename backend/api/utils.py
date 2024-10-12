import csv
from collections import defaultdict

from django.http import HttpResponse


def write_shopping_cart_file(user):
    """Write user's shopping cart in csv file."""
    ingredients = defaultdict(int)

    for cart_item in user.shopping_cart.all():
        recipe = cart_item.recipe
        for recipe_ingredient in recipe.recipeingredient_set.all():
            ingredients[
                (
                    recipe_ingredient.ingredient.name,
                    recipe_ingredient.ingredient.measurement_unit,
                )
            ] += recipe_ingredient.amount

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["Ingredient", "Measurement Unit", "Amount"])
        for (ingredient_name, measurement_unit), amount in ingredients.items():
            writer.writerow([ingredient_name, measurement_unit, amount])
        return response
