from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram import settings

from django.core.validators import RegexValidator


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(regex=r"^[\w.@+-]+$",
            message="Недопустимый символ")
        ],
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=200,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=200,
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
