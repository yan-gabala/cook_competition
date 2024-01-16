from django_filters import rest_framework as django_filters
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag

CHOICES = ((1, 1), (0, 0))


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author_id')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=CHOICES,
        method='filter_is_favorited')
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=CHOICES,
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == '0':
            return Recipe.objects.exclude(recipe__user=user).all()
        return Recipe.objects.filter(recipe__user=user).all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == '0':
            return Recipe.objects.exclude(recipe_sh__user=user).all()
        return Recipe.objects.filter(recipe_sh__user=user).all()
