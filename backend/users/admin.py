from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    """Класс пользователей."""

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'first_name',
                           'last_name', 'email'),
            },
        ),
    )
    list_filter = ('username', 'email')


admin.site.register(User, CustomUserAdmin)
