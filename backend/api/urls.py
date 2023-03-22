from django.urls import include, path, re_path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscribeViewSet,
                    SubscriptionViewSet, TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet, basename='subscribe'
)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionViewSet .as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
