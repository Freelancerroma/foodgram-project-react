import re

from django.core.exceptions import ValidationError


def validate_hex(hex):
    """Проверка цвета в HEX-формате."""

    if not re.fullmatch(r'^#[0-9A-F]{6}$', hex):
        raise ValidationError(
            'Цвет должен быть в HEX-формате.'
        )
