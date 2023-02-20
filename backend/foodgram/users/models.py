from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import MAX_LENGTH_FIELD


class User(AbstractUser):
    """Настраиваемая модель пользователя."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_LENGTH_FIELD,
        unique=True,
        validators=[RegexValidator(r'^[\w.@+-]+$',
                    ('Введенное имя пользователя недопустимо'))],
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_FIELD,
        blank=True, null=True,
        validators=[RegexValidator(r'^[а-яА-ЯёЁa-zA-Z]+$',
                    ('В поле "Имя" допускаются только буквы'))],
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_FIELD,
        blank=True, null=True,
        validators=[RegexValidator(r'^[а-яА-ЯёЁa-zA-Z]+$',
                    ('В поле "Фамилия" допускаются только буквы'))],
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
        return self.username

    def validate_username(username):
        if username == 'me':
            raise ValidationError(
                'Имя пользователя "me" не допустимо'
            )
        return username


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
