from core.utils import preparation_file
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http.response import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from users.models import Subscription

from api.exceptions import BadRequestException
from api.serializers import (FavoriteSerializer, IngredientsSerializer,
                             RecipesPostSerializer, RecipesSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             SubscriptionSerializer, TagsSerializer)
from api.viewsets import CreateDestroyViewSet, ListViewSet

from .filters import IngredientFilter, RecipeFilter

User = get_user_model()


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    ordering = ('name',)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    ordering = ('name',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.select_related("author")
        .prefetch_related('tags', 'ingredients_recipes')
        .all()
    )
    serializer_class = RecipesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipesPostSerializer
        return RecipesSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = '_' + request.user.username
        content_type = {'.txt': 'text/plain'}
        recipes = Recipe.objects.filter(recipe_sh__user=request.user)
        ingredients = IngredientRecipe.objects.filter(
            recipe__in=recipes).values(
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
                    amount=Sum('amount')).order_by('ingredient__name',
                                                   'amount')
        file = user
        preparation_file(file, settings.EXT, ingredients)
        return FileResponse(open(file + settings.EXT, 'rb'),
                            as_attachment=True,
                            content_type=content_type[settings.EXT])


class SubscriptionsViewSet(ListViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('author',)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(
            id__in=user.subscriber.values('author_id')).annotate(
            recipes_count=Count('recipes')
        )


class SubscribeViewSet(CreateDestroyViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        author = get_object_or_404(User, pk=self.kwargs['id'])
        subscriber = self.request.user
        return get_object_or_404(queryset, subscriber=subscriber,
                                 author=author)

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs['id'])
        serializer.save(subscriber=self.request.user, author=author)


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.select_related('user', 'recipe').all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('recipe',)

    def get_object(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['id'])
        user = self.request.user
        if not Favorite.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise BadRequestException(
                {'errors': 'Этого рецепта нет в избранном!'},)
        return get_object_or_404(Favorite, user=user,
                                 recipe=recipe)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['id'])
        serializer.save(user=self.request.user, recipe=recipe)


class ShoppingCartViewSet(CreateDestroyViewSet):
    queryset = ShoppingCart.objects.select_related('user', 'recipe').all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('recipe',)

    def get_object(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['id'])
        user = self.request.user
        if not ShoppingCart.objects.filter(user=user,
                                           recipe=recipe).exists():
            raise BadRequestException(
                {'errors': 'Этого рецепта нет в списке покупок!'})
        return get_object_or_404(ShoppingCart, user=user,
                                 recipe=recipe)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['id'])
        serializer.save(user=self.request.user, recipe=recipe)
