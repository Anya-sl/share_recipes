from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscription, User


class SingUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')


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
        return Subscription.objects.filter(following=obj, user=user).exists()


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в сокращенном формате."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для отображения подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return SubscribeRecipeSerializer(
            queryset, many=True).data


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
