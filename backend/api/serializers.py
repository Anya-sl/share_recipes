from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from core.validators import (validate_ingredients, validate_min_value,
                             validate_username)
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


def get_is_in_list(user, obj, model):
    """Проверить, есть ли рецепт в списке избранного или покупок."""
    return (user.is_authenticated
            and model.objects.filter(user=user, recipe=obj).exists())


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для любого пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли пользователь на авторов."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()

    def validate_username(self, username):
        validate_username(username)
        return username


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для указания количества ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddToIngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления количества ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('amount', 'id')
        validators = [validate_min_value]


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
    ingredients = IngredientAmountSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True,)
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

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate_ingredients(self, ingredients):
        validate_ingredients(ingredients)

    def create_ingredients(self, ingredients, recipe):
        IngredientAmount.objects.bulk_create([IngredientAmount(
            ingredient=ingredient['id'],
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
        instance.name = validated_data.pop('name', instance.name)
        instance.cooking_time = validated_data.pop(
            'cooking_time',
            instance.cooking_time,
        )
        instance.image = validated_data.pop('image', instance.image)
        ingredients = validated_data.pop('ingredients')
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.text = validated_data.pop('text', instance.text)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок."""

    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли пользователь на авторов."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(following=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit is not None:
            try:
                queryset = queryset[:int(recipes_limit)]
                return RecipeSerializer(queryset, many=True).data
            except ValueError:
                raise ValueError('Неверный формат данных')
        return RecipeSerializer(queryset, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения действий с подписками."""

    class Meta:
        model = Subscription
        fields = ('user', 'following')

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        if Subscription.objects.filter(
                user=self.context['request'].user,
                following=data['following']
        ):
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора')
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return SubscriptionSerializer(instance.following, context=context).data
