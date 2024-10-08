import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from a JSON file into the database"

    def handle(self, *args, **kwargs):
        with open("ingredients.json", encoding="utf-8") as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.create(
                    name=item["name"],
                    measurement_unit=item["measurement_unit"],
                )
            self.stdout.write(
                self.style.SUCCESS("Ingredients loaded successfully")
            )
