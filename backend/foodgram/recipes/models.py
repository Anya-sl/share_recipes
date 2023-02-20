import re

from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError

from foodgram.settings import MAX_LENGTH_FIELD
from users.models import User


class Ingredient(models.Model):
    """Класс, представляющий модель ингридиента."""

    measurement_unit = models.CharField(
        max_length=16,
        verbose_name='Единицы измерения',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_FIELD,
        db_index=True,
        verbose_name='Название',
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
        max_length=7,
        unique=True,
        verbose_name='Цветовой HEX-код',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_FIELD,
        unique=True, db_index=True,
        verbose_name='Название',
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

    def validate_color(self, color):
        if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color) is None:
            raise ValidationError(
                'Цвет должен быть в формте HEX')


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
        validators=[
            MinValueValidator(
                1,
                message="Время приготовления не может быть меньше минуты"
            )
        ],
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    # Не понимаю, как я могу использовать для ingredients что-то другое?
    # IngredientAmount у меня соделжит ссылку на Recipe - будет перекрестная
    # ссылка, я даже в голове не могу представить, что будет при этом 
    # происходить.
    # У меня же through='IngredientAmount' позволяет как раз вводить 
    # количество для ингредиентов, тем более в сериалайзерах используется
    # нужный класс везде IngredientAmount.
    # В админке я могу вводить количество ингридиента, благодяря этому
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
        verbose_name='Список ингредиентов',
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название',
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
        verbose_name='Количество ингредиентов'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'
