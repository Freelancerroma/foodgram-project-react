import re
# from .models import User
from django.core.exceptions import ValidationError


class ValidateUsername:
    """Валидация имени пользователя."""

    def validate_username(self, username):
        pattern = re.compile(r'^[\w.@+-]+\z')
        symbols_forbidden = re.sub(pattern, '', username)
        if symbols_forbidden:
            symbols = ", ".join(symbols_forbidden)
            raise ValidationError(
                f'Запрещенные символы symbols: {symbols}.'
            )
        if username == 'me':
            raise ValidationError(
                f'{username} не может быть me.'
            )
        # if User.objects.filter(username=username).exists():
        #     raise ValidationError(
        #         f'Username "{username}" недоступен.'
        #     )
        return username


# class ValidateEmail:
#     """Валидация почты пользователя на уникальность."""

#     def validate_email(self, email):
#         if User.objects.filter(email=email).exists():
#             raise ValidationError('Email недоступен.')
#         return email
