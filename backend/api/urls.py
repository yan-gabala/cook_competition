from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    SubscribeViewSet,
    SubscriptionsViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet
)


app_name = 'api'


router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet)

urlpatterns = [
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'})
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'})
    ),
    path(
        'users/subscriptions/', SubscriptionsViewSet.as_view({'get': 'list'})
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
