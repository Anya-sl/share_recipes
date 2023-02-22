import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data from static'

    def handle(self, *args, **kwargs):
        model_data = (
            (Ingredient, 'ingredients'),
        )
        try:
            for model, file in model_data:
                with open(
                    f'{settings.BASE_DIR}/static_backend/data/{file}.csv',
                    'r',
                    encoding='utf-8'
                ) as csv_file:
                    reader = csv.DictReader(csv_file)
                    model.objects.bulk_create(
                        objs=[model(**data) for data in reader],
                        ignore_conflicts=True
                    )
            print('Load data completed.')
        except FileNotFoundError:
            raise CommandError('Файл не найден')
