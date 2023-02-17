from django.contrib import admin

from .models import Ingredient, Recipe, Tag, IngredientAmount


class AmountIngredientForRecipeInLine(admin.TabularInline):
    model = IngredientAmount


class IngredientAdmin(admin.ModelAdmin):
    """Класс ингридентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    """Класс рецептов."""

    list_display = ('id', 'author', 'name', 'cooking_time')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    inlines = [AmountIngredientForRecipeInLine]
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    """Класс тэгов."""

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
