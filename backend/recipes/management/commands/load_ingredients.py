import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('./data/ingredients.json', 'rb') as f:
            data = json.load(f)
            for line in data:
                Ingredient.objects.get_or_create(
                    name=line['name'].lower(),
                    measurement_unit=line['measurement_unit'].lower(),
                )
