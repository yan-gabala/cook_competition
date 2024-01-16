from core.constants import Limits
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        max_length=Limits.MAX_LEN_EMAIL_FIELD.value,
        unique=True
    )
    password = models.CharField(
        _('password'),
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value
    )
    first_name = models.CharField(
        _('first name'),
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value
    )
    last_name = models.CharField(
        _('last name'),
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'поварёнок'
        verbose_name_plural = 'Все поварята'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique subscriber author'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='self susbscription'
            )
        ]

    def __str__(self):
        return f'Подписчик {self.subscriber} - автор {self.author}'
