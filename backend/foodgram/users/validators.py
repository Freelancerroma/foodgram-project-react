import re

from django.core.exceptions import ValidationError


class ValidateUsername:
    """Валидация имени пользователя."""

    def validate_username(self, username):
        pattern = re.compile(r'^[a-zA-Z0-9_.@+-]+$')
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
        return username
