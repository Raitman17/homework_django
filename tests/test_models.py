"""Модуль для тестов моделей."""

from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from hotel_app.models import Client, Hotel, Reserve, Room, Service


def create_model_test(model_class, valid_attrs: dict, bunch_of_invalid_attrs: tuple[dict] = None):
    """Создать тест модели.

    Args:
        model_class (_type_): класс модели
        valid_attrs (dict): корректные данные
        bunch_of_invalid_attrs (tuple[dict], optional): некорректные данные. по умолчанию None.

    Returns:
        _type_: Класс теста модели
    """
    class ModelTest(TestCase):
        def test_unsuccessful_creation(self):
            if bunch_of_invalid_attrs:
                for invalid_attrs in bunch_of_invalid_attrs:
                    with self.assertRaises(ValidationError):
                        model_class.objects.create(**invalid_attrs)

        def test_successful_creation(self):
            if model_class == Room:
                valid_attrs['hotel'] = Hotel.objects.create(name='abc', rating=4.4)
            model_class.objects.create(**valid_attrs)
    return ModelTest


HotelModelTest = create_model_test(
    Hotel,
    {'name': 'abc', 'rating': 4.4},
    ({'name': 'abc', 'rating': -4.4},
     {'name': 'abc', 'rating': 5.4})
)
ServiceModelTest = create_model_test(Service, {'name': 'abc'})
RoomModelTest = create_model_test(
    Room,
    {'category': 'double', 'floor': 2, 'number': 201, 'cost': 10},
    (
        {'category': 'abcd', 'floor': 2, 'number': 201, 'cost': 10},
        {'category': 'double', 'floor': 2, 'number': -201, 'cost': 10},
        {'category': 'double', 'floor': 2, 'number': 201, 'cost': -10},
    )
)


class ClientTest(TestCase):
    """Класс для тестов клиента."""

    def setUp(self) -> None:
        """Параметры."""
        self.user = User.objects.create(username='abc', first_name='abc', last_name='abc', password='abc')

    def test_invalid(self):
        """Тест на ошибку."""
        with self.assertRaises(ValidationError):
            Client.objects.create(user=self.user, money=-1)

    def test_create_and_str(self):
        """Тест на создание и метод стр."""
        self.assertEqual(str(Client.objects.create(user=self.user)), 'abc (abc abc)')


class ReserveTest(TestCase):
    """Класс для тестов бронирования."""

    def setUp(self) -> None:
        """Параметры."""
        user = User.objects.create(username='abc', first_name='abc', last_name='abc', password='abc')
        self.client = Client.objects.create(user=user)
        hotel = Hotel.objects.create(name='abc', rating=4.4)
        self.room = Room.objects.create(category='double', floor=4, number=5, hotel=hotel)
        self.reserve_data = {
                'user': self.client,
                'room': self.room,
                'start_date': date(2030, 7, 17),
                'end_date': date(2030, 7, 20),
                'price': 20
        }

    def test_invalid(self):
        """Тесты на ошибки."""
        with self.assertRaises(ValidationError):
            Reserve.objects.create(**self.reserve_data)
            Reserve.objects.create(**self.reserve_data)
        with self.assertRaises(ValidationError):
            self.reserve_data['start_date'] = date(2010, 7, 17)
            Reserve.objects.create(**self.reserve_data)
        with self.assertRaises(ValueError):
            self.reserve_data['room'] = 'dfhjdfd'
            Reserve.objects.create(**self.reserve_data)
        with self.assertRaises(ValidationError):
            self.reserve_data['price'] = -20
            Reserve.objects.create(**self.reserve_data)

    def test_create_and_str(self):
        """Тест на создание и метод стр."""
        self.assertEqual(str(Reserve.objects.create(**self.reserve_data)), 'abc 5 2030-07-20')
