from django.db.models import Count, F, Prefetch
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription, User


class GetIsSubscribedMixin:
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj.id).exists()


class CustomUserSerializer(GetIsSubscribedMixin, UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        read_only_fields = ('is_subscribed',)


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'measurement_unit', 'id')
        model = Ingredient


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    ingredients = IngredientRecipeSerializer(source='ingredients_recipes',
                                             many=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(
        required=False, allow_null=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        return (self.context.get('request').user.is_authenticated
                and Favorite.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())


class RecipeMinifiedSerializer(RecipesSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetIngredientsMixin:

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_recipes__amount')
        )


class RecipesPostSerializer(GetIngredientsMixin, serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_tags(self, tags):
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Повтор тега'
                )
            tags_list.append(tag)
            if len(tags_list) < 1:
                raise serializers.ValidationError(
                    'Выберите тег'
                )
        return tags

    def validate(self, data):
        name = data.get('name')
        if len(name) < 2:
            raise serializers.ValidationError({
                'name': 'Название рецепта минимум 2 символа'})
        ingredients = self.initial_data['ingredients']
        ingredient_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Минимально должен быть 1 ингредиент.'
            )
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент не должен повторяться.'
                )
            if int(item.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Минимальное количество = 1'
                )
            ingredient_list.append(ingredient)
        data['ingredients'] = ingredients
        return data

    def add_ingredients_and_tags(self, instance, **validate_data):
        ingredients = validate_data['ingredients']
        tags = validate_data['tags']
        for tag in tags:
            instance.tags.add(tag)

        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ])
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        return self.add_ingredients_and_tags(
            recipe, ingredients=ingredients, tags=tags
        )

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = self.add_ingredients_and_tags(
            instance, ingredients=ingredients, tags=tags)
        return super().update(instance, validated_data)


class SubscriptionSerializer(CustomUserSerializer):
    recipes = RecipeMinifiedSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ()  # python пишет, что поле должно быть
        model = Subscription

    def validate(self, data):
        request = self.context.get('request')
        author = get_object_or_404(
            User, pk=self.context.get('view').kwargs.get('id')
        )
        subscriber = request.user
        if request.method == 'POST':
            if author == subscriber:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя!'
                )
            if Subscription.objects.filter(
                author=author, subscriber=subscriber
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора!'
                )
        return data

    def to_representation(self, instance):
        user_query = User.objects.all().annotate(
            recipes_count=Count("recipes")
        )
        sub_query = Subscription.objects.select_related(
            'subscriber').prefetch_related(
                Prefetch("author", queryset=user_query)
        )
        instance = get_object_or_404(
            sub_query, subscriber=instance.subscriber, author=instance.author
        )
        serializer = SubscriptionSerializer(instance.author,
                                            context=self.context)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ()
        model = Favorite

    def validate(self, data):
        request = self.context.get('request')
        recipe = get_object_or_404(
            Recipe,
            pk=self.context.get('view').kwargs.get('id')
        )
        user = request.user
        if (request.method == 'POST'
            and Favorite.objects.filter(recipe=recipe,
                                        user=user).exists()):
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном!')
        return data

    def to_representation(self, instance):
        serializer = RecipeMinifiedSerializer(instance.recipe)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ()
        model = ShoppingCart

    def validate(self, data):
        request = self.context.get('request')
        recipe = get_object_or_404(
            Recipe,
            pk=self.context.get('view').kwargs.get('id')
        )
        user = request.user
        if (request.method == 'POST'
            and ShoppingCart.objects.filter(recipe=recipe,
                                            user=user).exists()):
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок!')
        return data

    def to_representation(self, instance):
        serializer = RecipeMinifiedSerializer(instance.recipe)
        return serializer.data
