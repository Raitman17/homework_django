"""Модуль для форм."""
from django.contrib.auth import forms, models
from django.core.exceptions import ValidationError
from django.forms import (CharField, DateField, DateInput, DecimalField,
                          EmailField, Form)

DECIMAL_PACES = 2
MAX_DIGITS = 11
EMAIL_MAX_LENGTH = 200


class DateInputField(DateInput):
    """Поле ввода даты."""

    input_type = 'date'


class RegistrationForm(forms.UserCreationForm):
    """Форма регистрации."""

    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = EmailField(max_length=EMAIL_MAX_LENGTH, required=True)

    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class AddFundsForm(Form):
    """Форма добавления средств."""

    money = DecimalField(label='money', decimal_places=DECIMAL_PACES, max_digits=MAX_DIGITS)

    def is_valid(self) -> bool:
        """Проверка формы.

        Returns:
            bool: истина/ложь
        """
        def add_error(error: str):
            """Добавить ошибку.

            Args:
                error (str): сообщение ошибки
            """
            if self.errors:
                self.errors['money'] += [error]
            else:
                self.errors['money'] = [error]

        if not super().is_valid():
            return False
        money = self.cleaned_data.get('money', None)
        if not money:
            add_error(ValidationError('an error occured, money field was not specified!'))
            return False
        if money < 0:
            add_error(ValidationError('you can only add positive amount of money!'))
            return False
        return True


class BookRoom(Form):
    """Форма для полей даты."""

    start_date = DateField(label='start_date', widget=DateInputField)
    end_date = DateField(label='end_date', widget=DateInputField)
