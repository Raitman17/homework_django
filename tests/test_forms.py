"""Модуль тестов для форм."""

from django.contrib.auth.models import User
from django.test import TestCase

from hotel_app.forms import AddFundsForm, RegistrationForm

valid_data = {
    'username': 'abc',
    'first_name': 'abc',
    'last_name': 'abc',
    'email': 'email@email.com',
    'password1': 'tArAs0ff2005',
    'password2': 'tArAs0ff2005',
}

not_matching_password = valid_data.copy()
not_matching_password['password2'] = 'abc'

invalid_email = valid_data.copy()
invalid_email['email'] = 'abc'

short_password = valid_data.copy()
short_password['password1'] = 'abc'
short_password['password2'] = 'abc'

common_password = valid_data.copy()
common_password['password1'] = 'abcdef123'
common_password['password2'] = 'abcdef123'


class TestRegistrationForm(TestCase):
    """Класс тестов для регистрационной формы."""

    def test_valid(self):
        """Тест на валидность."""
        self.assertTrue(RegistrationForm(data=valid_data).is_valid())

    def test_not_matching_passwords(self):
        """Тест на неодинаковые пароли."""
        self.assertFalse(RegistrationForm(data=not_matching_password).is_valid())

    def test_short_password(self):
        """Тест на короткий пароль."""
        self.assertFalse(RegistrationForm(data=short_password).is_valid())

    def test_invalid_email(self):
        """Тест на неправильную почту."""
        self.assertFalse(RegistrationForm(data=invalid_email).is_valid())

    def test_common_password(self):
        """Тест на популярный пароль."""
        self.assertFalse(RegistrationForm(data=common_password).is_valid())

    def test_existing_user(self):
        """Тест на существующего пользователя."""
        User.objects.create(username=valid_data['username'], password='abc')
        self.assertFalse(RegistrationForm(data=valid_data).is_valid())


class TestAddFundsForm(TestCase):
    """Класс для тестов на добавление средств."""

    def test_valid(self):
        """Тест на валидность с целым числом."""
        self.assertTrue(AddFundsForm(data={'money': 100}).is_valid())

    def test_negative(self):
        """Тест на отрицательное число."""
        self.assertFalse(AddFundsForm(data={'money': -100}).is_valid())

    def test_invalid_decimal_fields(self):
        """Тест на ограничение знаков после запятой."""
        self.assertFalse(AddFundsForm(data={'money': 100.123}).is_valid())

    def test_valid_decimal_fields(self):
        """Тест на валидность с нецелым числом."""
        self.assertTrue(AddFundsForm(data={'money': 100.12}).is_valid())

    def test_invalid_max_digits(self):
        """Тест на максимальное число."""
        self.assertFalse(AddFundsForm(data={'money': 123456789123}).is_valid())
