"""recipes/models.py"""


from colorfield.fields import ColorField
from core.constants import Limits
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Обозначение ингредиента',
        max_length=Limits.DESIGNATION.value
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=Limits.DESIGNATION.value
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_among_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Наименование тега',
        max_length=Limits.DESIGNATION.value,
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет',
        default='#FFFFFF'
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        max_length=Limits.DESIGNATION.value,
        null=True,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'В какое время подавать'
        verbose_name = 'в какое время подавать'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='В какое время подавать'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Имя поварёнка'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=Limits.DESIGNATION.value,
        verbose_name='Название',
        validators=[
            RegexValidator(
                regex='[a-zа-я]+',
                message='Принимаются слова из букв'
            )
        ]
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Вариант сервировки'
    )
    text = models.TextField(
        verbose_name='Как приготовить'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=[
            MinValueValidator(
                Limits.MIN_COOKING_TIME.value,
                'Время приготовления не может быть меньше 1 минуты'
            ),
            MaxValueValidator(
                Limits.MAX_COOKING_TIME.value,
                'Ошибка ввода времени приготовления'
            )
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                Limits.MIN_AMOUNT_INGREDIENTS.value,
                'Нельзя выбрать < 1'
            ),
            MaxValueValidator(
                Limits.MAX_AMOUNT_INGREDIENTS,
                'Нельзя выбрать > 20'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        ordering = ('-recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe}: ' f'({self.ingredient}) - {self.amount}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэг для рецепта'
        verbose_name_plural = 'Тэги для рецепта'
        ordering = ('-recipe',)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class AbstractUserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class ShoppingCart(AbstractUserRecipe):

    class Meta:
        default_related_name = 'recipe_sh'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique user_sh recipe_sh')
        ]

    def __str__(self):
        return (f'Пользователь {ShoppingCart.user} добавил'
                f'рецепт в корзину {ShoppingCart.recipe}')


class Favorite(AbstractUserRecipe):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )

    class Meta:
        default_related_name = 'recipe'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique user recipe')
        ]

        def __str__(self):
            return (f'Пользователь {Favorite.user} добавил'
                    f'рецепт в корзину {Favorite.recipe}')
