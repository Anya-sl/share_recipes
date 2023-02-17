import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data from static'

    def handle(self, *args, **kwargs):
        model_data = (
            (Ingredient, 'ingredients'),
        )
        for model, file in model_data:
            with open(
                f'{settings.BASE_DIR}/static/data/{file}.csv',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(
                    model(**data) for data in reader)
        print('Load data completed.')
