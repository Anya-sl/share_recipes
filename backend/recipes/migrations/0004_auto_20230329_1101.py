# Generated by Django 2.2 on 2023-03-29 11:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230325_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientamount',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Значение не может быть меньше 1')], verbose_name='Количество ингредиентов'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Значение не может быть меньше 1')], verbose_name='Время приготовления (в минутах)'),
        ),
    ]