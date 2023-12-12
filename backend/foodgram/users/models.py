from django.db import models
from django.contrib.auth.models import AbstractUser
from foodgram import settings
from .validators import ValidateUsername


class User(ValidateUsername, AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.USERNAME_LEN,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=settings.EMAIL_LEN,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.FIRST_NAME_LEN,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LAST_NAME_LEN,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.email


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='Подписаться можно только один раз на одного автора.'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='Нельзя подписаться на самого себя.'
            ),
        ]
