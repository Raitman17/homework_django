"""Модуль для тестов бронирования."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import client as test_client

from hotel_app.models import Client, Hotel, Room


class TestReserve(TestCase):
    """Тесты бронирования."""

    _reserve_page = '/reserve/'

    def setUp(self) -> None:
        """Параметры."""
        self.test_client = test_client.Client()
        self.user = User.objects.create(username='user', password='user')
        self.hotel_client = Client.objects.create(user=self.user)
        self.test_client.force_login(self.user)

        hotel = Hotel.objects.create(name='abc', address='abc', rating=4.4)
        self.room = Room.objects.create(category='business', floor=10, number=111, hotel=hotel, cost=10)
        self.page_url = f'{self._reserve_page}?id={self.room.id}'

    def test_insufficient_funds(self):
        """Тест недостаточно средств."""
        self.test_client.post(self.page_url, {'start_date': '2025-07-20', 'end_date': '2025-07-21'})
        self.assertEqual(self.hotel_client.money, 0)
        self.assertNotIn(self.room, self.hotel_client.rooms.all())

    def test_book_a_room(self):
        """Тест бронирование номера."""
        self.hotel_client.money = 10
        self.hotel_client.save()

        self.test_client.post(self.page_url, {'start_date': '2025-07-20', 'end_date': '2025-07-21'})
        self.hotel_client.refresh_from_db()

        self.assertEqual(self.hotel_client.money, 0)
        self.assertIn(self.room, self.hotel_client.rooms.all())

    def test_repeated_book_a_room(self):
        """Тест на повторное бронирования номера."""
        self.hotel_client.money = 20
        self.hotel_client.save()

        self.test_client.post(self.page_url, {'start_date': '2025-07-20', 'end_date': '2025-07-21'})
        self.test_client.post(self.page_url, {'start_date': '2025-07-20', 'end_date': '2025-07-21'})
        self.hotel_client.refresh_from_db()

        self.assertEqual(self.hotel_client.money, 10)
        reserved_client_rooms = self.hotel_client.rooms.filter(id=self.room.id)
        self.assertEqual(len(reserved_client_rooms), 1)

        self.test_client.post(self.page_url, {'start_date': '2025-07-25', 'end_date': '2025-07-26'})
        self.hotel_client.refresh_from_db()
        self.assertEqual(self.hotel_client.money, 0)
        reserved_client_rooms = self.hotel_client.rooms.filter(id=self.room.id)
        self.assertEqual(len(reserved_client_rooms), 2)
