import re

from django.core.exceptions import ValidationError


def validate_username(username):
    pattern = re.compile(r'^[\w.@+-]+\Z')
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
