from django.db.models.aggregates import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientsFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          SubscribeSerializer, SubscriptionSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


def post_delete_favorite_shopping_cart(request, model, id):
    """Добавить или удалить в список покупок или избранное."""
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# class SubscribeViewSet(viewsets.ModelViewSet):

#     queryset = User.objects.all()
#     permission_classes = (IsAuthenticated,)

#     def create(self, request, *args, **kwargs):
#         """Подписаться на автора."""
#         serializer = SubscribeSerializer(
#             data={'user': request.user.id,
#                   'following': self.kwargs.get('user_id')},
#             context={'request': request},
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def destroy(self, request, *args, **kwargs):
#         """Отписаться от автора."""
#         follow = get_object_or_404(
#             Subscription,
#             user=request.user,
#             following=get_object_or_404(User, id=self.kwargs.get('user_id')),
#         )
#         follow.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class SubscriptionViewSet(viewsets.ModelViewSet):

#     queryset = User.objects.all()
#     permission_classes = (IsAuthenticated,)

#     def list(self, request):
#         """Получить список подписок текущего пользователя."""
#         user = get_object_or_404(
#             User,
#             id=request.user.id
#         )
#         queryset = user.follower.all()
#         serializer = SubscriptionSerializer(
#             queryset,
#             many=True,
#             context={'request': request}
#         )
#         return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<id>[\d]+)/favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, id):
        """Добавить или удалить в избранное."""
        return post_delete_favorite_shopping_cart(request, Favorite, id)

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<id>[\d]+)/shopping_cart',
        url_name='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, id):
        """Добавить или удалить в список покупок."""
        return post_delete_favorite_shopping_cart(request, ShoppingCart, id)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список с ингредиентами."""
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(total=Sum('amount'))
        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["total"]}'
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
