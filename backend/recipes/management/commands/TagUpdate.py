import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = "Load ingredients from a JSON file into the database"

    def handle(self, *args, **kwargs):
        with open("tags.json", encoding="utf-8") as file:
            data = json.load(file)
            for item in data:
                Tag.objects.create(name=item["name"], slug=item["slug"])
            self.stdout.write(self.style.SUCCESS("Tags loaded successfully"))
