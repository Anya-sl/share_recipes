from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator

validate_letter_field = RegexValidator(r'^[а-яА-ЯёЁa-zA-Z\s]+$',
                                       ('Поле может содержать только буквы'))

validate_hex = RegexValidator(r'^#([0-9a-fA-F]){3,6}$',
                              ('Цвет должен быть в формте HEX'))

validate_min_value = MinValueValidator(
    1,
    message="Значение не может быть меньше 1"
)


def validate_username(value):
    if value.lower == 'me':
        raise ValidationError(
            'Имя пользователя "me" не допустимо'
        )
    return value


def validate_ingredients(ingredients):
    for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 1')
    return ingredients
