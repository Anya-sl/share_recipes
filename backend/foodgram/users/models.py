from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Настраиваемая модель пользователя."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True, null=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True, null=True,
    )

    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    def __str__(self):
        return f'{self.username}'


class Subscription(models.Model):
    """Класс, представляющий модель подписки на автора."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='following_unique',
                fields=('user', 'following'),
            ),
        ]
