from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    change_user_password_template = True
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_superuser',
        'is_staff',
        'is_active',
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'author')
    search_fields = ('subscriber', 'author')
    list_filter = ('subscriber', 'author')
