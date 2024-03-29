# Generated by Django 2.2 on 2023-03-25 10:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230315_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, null=True, validators=[django.core.validators.RegexValidator('^[а-яА-ЯёЁa-zA-Z\\s]+$', 'Поле может содержать только буквы')], verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, null=True, validators=[django.core.validators.RegexValidator('^[а-яА-ЯёЁa-zA-Z\\s]+$', 'Поле может содержать только буквы')], verbose_name='Фамилия'),
        ),
    ]
