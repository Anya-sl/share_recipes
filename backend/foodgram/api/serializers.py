import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.serializers import UserSerializer


def get_is_in_list(user, obj, model):
    if (
        user.is_authenticated
        and model.objects.filter(user=user, recipe=obj).exists()
    ):
        return True
    return False


class Base64ImageField(serializers.ImageField):
    """Сериализатор для поля картинки."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'ingredient', 'recipe', 'amount')


class AddToIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('amount', 'id')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в сокращенном формате."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (только для чтения)."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredientamount_set',
        read_only=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        return get_is_in_list(self.context.get('request').user, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return get_is_in_list(
            self.context.get('request').user, obj, ShoppingCart)


class RecipeWriteSerializer(RecipeReadSerializer):
    """Сериализатор для рецептов (POST, PATCH, DEL)."""

    image = Base64ImageField()
    ingredients = AddToIngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def create_ingredients(self, recipe, ingredients):
        IngredientAmount.objects.bulk_create([IngredientAmount(
            ingredient=ingredient['ingredient'],
            recipe=recipe,
            amount=ingredient['amount']
        ) for ingredient in ingredients])

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        user = self.context.get('request').user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        instance.cooking_time = validated_data.pop(
            'cooking_time',
            instance.cooking_time,
        )
        instance.image = validated_data.pop('image', instance.image)
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        instance.name = validated_data.pop('name', instance.name)
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.text = validated_data.pop('text', instance.text)
        return super().update(instance, validated_data)
