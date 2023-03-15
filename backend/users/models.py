from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from core.validators import validate_letter_field, validate_username
from foodgram.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_FIELD


class User(AbstractUser):
    """Настраиваемая модель пользователя."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_LENGTH_FIELD,
        blank=True, null=True,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username],
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_FIELD,
        blank=True, null=True,
        validators=[validate_letter_field],
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_FIELD,
        blank=True, null=True,
        validators=[validate_letter_field],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

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
        return self.username


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
            models.CheckConstraint(
                name='No self sibscription',
                check=~models.Q(following=models.F('user')),
            ),
            models.UniqueConstraint(
                name='following_unique',
                fields=('user', 'following'),
            ),
        ]
