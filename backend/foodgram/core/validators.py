from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator

validate_letter_feild = RegexValidator(r'^[а-яА-ЯёЁa-zA-Z]+$',
                                       ('Поле может содержать только буквы'))

validate_hex = RegexValidator(r'^#([0-9a-fA-F]){3,6}$',
                              ('Цвет должен быть в формте HEX'))

validate_min_value = MinValueValidator(
    1,
    message="Время приготовления не может быть меньше минуты"
)


def validate_username(value):
    if value.lower == 'me':
        raise ValidationError(
            'Имя пользователя "me" не допустимо'
        )
    return value
