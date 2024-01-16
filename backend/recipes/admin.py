from django.utils.html import format_html
from django.contrib import admin
from django.contrib.admin import TabularInline

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)


class IngredientInline(TabularInline):
    model = IngredientRecipe
    extra = 2


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ['name']
    list_per_page = 20
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_color')

    @admin.display(description='Цвет')
    def get_color(self, obj):
        return format_html(
            f'<spawn style="color: {obj.color};">{obj.color}</spawn>'
        )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'pub_date',
        'text',
        'cooking_time',
        'author',
        'image',
    )
    list_display_links = ('name', 'pub_date', 'text', 'cooking_time', 'author')
    list_editable = ('image',)
    list_per_page = 15
    filter_horizontal = ('tags',)
    search_fields = ['name']
    list_filter = ('author', 'tags')
    ordering = ('pub_date',)
    inlines = (IngredientInline,)

    @admin.display(description='Добавили в избранное', ordering='author')
    def count_favorite(self, obj):
        return obj.recipe.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
