from django.db import models

from core.validators import (validate_hex, validate_letter_field,
                             validate_min_value, validate_amount)
from foodgram.settings import MAX_LENGTH_FIELD, MAX_LENGTH_HEX, MAX_LENGTH_UOM
from users.models import User


class Ingredient(models.Model):
    """Класс, представляющий модель ингридиента."""

    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_UOM,
        verbose_name='Единицы измерения',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_FIELD,
        db_index=True,
        verbose_name='Название',
        validators=[validate_letter_field],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Класс, представляющий модель тэга."""

    color = models.CharField(
        max_length=MAX_LENGTH_HEX,
        unique=True,
        verbose_name='Цветовой HEX-код',
        validators=[validate_hex],
    )
    name = models.CharField(
        max_length=MAX_LENGTH_FIELD,
        unique=True, db_index=True,
        verbose_name='Название',
        validators=[validate_letter_field],
    )
    slug = models.SlugField(
        unique=True, db_index=True,
        verbose_name='slug',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Класс, представляющий модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[validate_min_value],
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_FIELD,
        db_index=True,
        verbose_name='Название',
        validators=[validate_letter_field],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True, db_index=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )
    text = models.TextField(
        verbose_name='Описание',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                name='author_recipe_unique',
                fields=('author', 'name'),
            ),
        ]

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Класс, представляющий модель избранных рецептов."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Владелец',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Избранные рецепты',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='favorites_unique',
                fields=('user', 'recipe'),
            ),
        ]


class ShoppingCart(models.Model):
    """Класс, представляющий модель рецептов, выбранных к покупке."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Владелец',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Рецепты к покупке',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='buying_unique',
                fields=('user', 'recipe'),
            ),
        ]


class IngredientAmount(models.Model):
    """Класс, представляющий количество ингридиента в рецепте."""

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        validators=[validate_amount],
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'
