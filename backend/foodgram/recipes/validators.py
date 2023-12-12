import re

from django.core.exceptions import ValidationError


class ValidateColor:
    """Проверка цвета в HEX-формате."""

    def validate_hex(hex):
        if not re.fullmatch(r'^#[0-9A-F]{6}$', hex):
            raise ValidationError(
                'Цвет должен быть в HEX-формате.'
            )
