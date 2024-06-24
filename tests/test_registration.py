"""Модуль для тестов на регистрацию."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import client as test_client


class TestRegistration(TestCase):
    """Класс для тестов регистрации."""

    _url = '/register/'
    _valid_creds = {
        'username': 'user',
        'password1': 'jo34r430d04j4dj3jdj2jd24d',
        'password2': 'jo34r430d04j4dj3jdj2jd24d',
        'first_name': 'Илья',
        'last_name': 'Прогульщик',
        'email': 'sleeping_till_13_oclock@pyaterki.net',
    }

    def setUp(self):
        """Параметры."""
        self.client = test_client.Client()

    def test_invalid(self):
        """Тест с некорректными данными."""
        invalid_creds = self._valid_creds.copy()
        invalid_creds['password1'] = 'abc'
        self.client.post(self._url, invalid_creds)
        self.assertEqual(len(User.objects.filter(username='user')), 0)

    def test_valid(self):
        """Тест с корректными данными."""
        self.client.post(self._url, self._valid_creds)
        self.assertEqual(len(User.objects.filter(username='user')), 1)
