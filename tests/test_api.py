"""Модуль для тестирования апи."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from hotel_app.models import Client, Hotel, Reserve, Room, Service


def create_viewset_test(model_class, url: str, creation_attrs: dict):
    """Создать тест.

    Args:
        model_class (_type_): класс модели
        url (str): ссылка
        creation_attrs (dict): словарь с атрибутами модели

    Returns:
        _type_: тест для апи модели
    """
    class ViewSetTest(TestCase):
        def setUp(self):
            """Параметры."""
            self.client = APIClient()
            self.hotel_obj = Hotel.objects.create(name='A', rating=4.1)
            self.room_obj = Room.objects.create(category='business', floor=10, number=111, hotel=self.hotel_obj)
            self.user = User.objects.create_user(username='user', password='user')
            self.superuser = User.objects.create_user(
                username='superuser', password='superuser', is_superuser=True,
            )
            self.user_token = Token.objects.create(user=self.user)
            self.superuser_token = Token.objects.create(user=self.superuser)

        def get(self, user: User, token: Token):
            """Получить.

            Args:
                user (User): пользователь
                token (Token): токен
            """
            self.client.force_authenticate(user=user, token=token)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_get_by_user(self):
            """Тест на метод get для обычного пользователя."""
            self.get(self.user, self.user_token)

        def test_get_by_superuser(self):
            """тест на метод get для админа."""
            self.get(self.superuser, self.superuser_token)

        def manage(self, user: User, token: Token, post_status: int, put_status: int, delete_status: int):
            """Тесты на создание, обновление и удаление объектов.

            Args:
                user (User): пользователь
                token (Token): токен
                post_status (int): пост статус код
                put_status (int): пут статус код
                delete_status (int): статус код для удаления
            """
            self.client.force_authenticate(user=user, token=token)

            if model_class == Room:
                creation_attrs['hotel'] = self.hotel_obj
            if model_class == Reserve:
                creation_attrs['user'] = Client.objects.create(user=self.user)
                creation_attrs['room'] = self.room_obj

            created_id = model_class.objects.create(**creation_attrs).id

            if model_class == Room:
                creation_attrs['hotel'] = f'http://127.0.0.1:8000/rest/hotels/{self.hotel_obj.id}/'
            if model_class == Reserve:
                creation_attrs['user'] = creation_attrs['user'].id
                creation_attrs['room'] = self.room_obj.id
                creation_attrs['start_date'] = '2025-07-17'
                creation_attrs['end_date'] = '2025-07-19'

            # POST
            response = self.client.post(url, creation_attrs)
            self.assertEqual(response.status_code, post_status)

            if model_class == Reserve:
                creation_attrs['start_date'] = '2025-07-20'
                creation_attrs['end_date'] = '2025-07-22'

            # PUT
            response = self.client.put(f'{url}{created_id}/', creation_attrs)
            self.assertEqual(response.status_code, put_status)

            # DELETE
            response = self.client.delete(f'{url}{created_id}/')
            self.assertEqual(response.status_code, delete_status)

        def test_manage_user(self):
            """Тест для обычного пользователя."""
            self.manage(
                user=self.user, token=self.user_token,
                post_status=status.HTTP_403_FORBIDDEN,
                put_status=status.HTTP_403_FORBIDDEN,
                delete_status=status.HTTP_403_FORBIDDEN,
            )

        def test_manage_superuser(self):
            """Тест для админа."""
            self.manage(
                user=self.superuser, token=self.superuser_token,
                post_status=status.HTTP_201_CREATED,
                put_status=status.HTTP_200_OK,
                delete_status=status.HTTP_204_NO_CONTENT,
            )

    return ViewSetTest


HotelViewSetTest = create_viewset_test(
    Hotel, '/rest/hotels/',
    {'name': 'A', 'rating': 4.1}
)

ServiceViewSetTest = create_viewset_test(
    Service, '/rest/services/',
    {'name': 'A'}
)

RoomViewSetTest = create_viewset_test(
    Room, '/rest/rooms/',
    {'category': 'business', 'floor': 8, 'number': 401}
)

RoomViewSetTest = create_viewset_test(
    Reserve, '/rest/reserve/',
    {'start_date': '2025-07-11', 'end_date': '2025-07-15', 'price': 10}
)
