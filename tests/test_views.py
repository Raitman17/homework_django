"""Модуль для тестов представления."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client as TestClient
from django.urls import reverse
from rest_framework import status

from hotel_app.models import Client, Hotel, Reserve, Room


def create_method_with_auth(url: str, page_name: str, template: str, login=False):
    """Создать метод с аутентификацией.

    Args:
        url (str): ссылка
        page_name (str): имя страницы
        template (str): шаблон
        login (bool): истина/ложь. по умолчанию False.

    Returns:
        _type_: метод
    """
    def method(self):
        """Метод.

        Args:
            self (_type_): ...
        """
        self.client = TestClient()
        if login:
            user = User.objects.create(username='user', password='user')
            Client.objects.create(user=user)
            self.client.force_login(user=user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template)

        response = self.client.get(reverse(page_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    return method


casual_pages = (
    ('', 'homepage', 'index.html'),
    ('/register/', 'register', 'registration/register.html'),
    ('/accounts/login/', 'login', 'registration/login.html'),
    ('/book_by_date/', 'book_by_date', 'book_by_date.html'),
)

methods_with_auth = {'test_profile': create_method_with_auth(*('/profile/', 'profile', 'profile.html'), login=True)}
TestWithAuth = type('TestWithAuth', (TestCase,), methods_with_auth)

casual_methods = {f'test_with_auth_{page[1]}': create_method_with_auth(*page, login=True) for page in casual_pages}
casual_methods.update({f'test_no_auth_{page[1]}': create_method_with_auth(*page, login=False) for page in casual_pages})
TestCasualPage = type('TestCasualPages', (TestCase,), casual_methods)


def create_method_no_auth(url: str):
    """Создать метод без аутентификации.

    Args:
        url (str): ссылка

    Returns:
        _type_: метод
    """
    def method(self):
        """Метод.

        Args:
            self (_type_): ...
        """
        self.client = TestClient()
        self.assertEqual(self.client.get(url).status_code, status.HTTP_302_FOUND)
    return method


methods_no_auth = {f'test_{url}': create_method_no_auth(url) for url in ('/profile/', '/reserve/')}
TestNoAuth = type('TestNoAuth', (TestCase,), methods_no_auth)


def create_method_instance(url: str, page_name: str, template: str, model, creation_attrs: dict):
    """Создать метод экземпляра.

    Args:
        url (str): ссылка
        page_name (str): имя траницы
        template (str): шаблон
        model (_type_): класс модели
        creation_attrs (dict): словарь с атрибутами

    Returns:
        _type_: метод
    """
    def method(self):
        """Метод.

        Args:
            self (_type_): ...
        """
        self.client = TestClient()
        user = User.objects.create(username='user', password='user')
        Client.objects.create(user=user)
        if model == Room:
            creation_attrs['hotel'] = Hotel.objects.create(name='abc', address='abc', rating=4.4)

        # GET without auth
        self.assertEqual(self.client.get(url).status_code, status.HTTP_302_FOUND)
        # login for client, test with auth below
        self.client.force_login(user=user)
        # GET without id
        self.assertEqual(self.client.get(url).status_code, status.HTTP_302_FOUND)
        # GET with invalid id
        self.assertEqual(self.client.get(f'{url}?id=123').status_code, status.HTTP_302_FOUND)
        # creating model object for using in url
        created_id = model.objects.create(**creation_attrs).id
        created_url = f'{url}?id={created_id}'
        created_reversed_url = f'{reverse(page_name)}?id={created_id}'
        # GET with valid id
        response = self.client.get(created_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template)
        self.assertEqual(self.client.get(created_reversed_url).status_code, status.HTTP_200_OK)

    return method


instance_pages = (
    ('/hotel/', 'hotel', 'hotel.html', Hotel, {'name': 'abc', 'address': 'abc', 'rating': 4.4}),
    ('/room/', 'room', 'room.html', Room, {'category': 'double', 'floor': 2, 'number': 201, 'cost': 10}),
    ('/reserve/', 'reserve', 'reserve.html', Room, {'category': 'double', 'floor': 2, 'number': 201, 'cost': 10}),
)

methods_intance = {f'test_{page[1]}': create_method_instance(*page) for page in instance_pages}
TestInstancePages = type('TestInstancePages', (TestCase,), methods_intance)


class TestDeleteReserve(TestCase):
    """Класс тестов для удаления бронирования."""

    def setUp(self) -> None:
        """Параметры."""
        hotel = Hotel.objects.create(name='abc', address='abc', rating=4.4)
        room = Room.objects.create(category='business', floor=10, number=111, hotel=hotel)
        self.client = TestClient()
        user = User.objects.create(username='user', password='user')
        self.client_test = Client.objects.create(user=user)
        self.client.force_login(user=user)
        self.reserve = Reserve.objects.create(
            user=self.client_test, room=room,
            start_date='2025-07-19', end_date='2025-07-29', price=100
        )

    def test_valid(self):
        """Тест с корректными данными."""
        self.assertEqual(self.client.get(f'/delete_reserve/?id={self.reserve.id}').status_code, status.HTTP_302_FOUND)
        self.assertFalse(Reserve.objects.filter(user=self.client_test))

    def test_invalid(self):
        """Тест с некорректными данными."""
        self.assertEqual(self.client.get('/delete_reserve/?id=123').status_code, status.HTTP_302_FOUND)
        self.assertTrue(Reserve.objects.filter(user=self.client_test))
