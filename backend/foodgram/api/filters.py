from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(shopping_cart__user=self.request.user)
