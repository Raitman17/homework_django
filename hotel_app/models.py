"""Модуль для модулей."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

NAMES_MAX_LENGTH = 100
IMAGE_MAX_LENGTH = 500
ADDRESS_MAX_LENGTH = 250
DESCRIPTION_MAX_LENGTH = 1000


def get_datetime() -> datetime:
    """Получить текущее время.

    Returns:
        datetime: текущее время
    """
    return datetime.now(timezone.utc)


def check_created(dt: datetime) -> None:
    """Проверить дату создания.

    Args:
        dt (datetime): дата

    Raises:
        ValidationError: ошибка
    """
    if dt > get_datetime():
        raise ValidationError(_('Datetime is bigger than current datetime!'))


def check_modified(dt: datetime) -> None:
    """Проверить дату обновления.

    Args:
        dt (datetime): дата

    Raises:
        ValidationError: ошибка
    """
    if dt > get_datetime():
        raise ValidationError(_('Datetime is bigger than current datetime!'))


def check_date(dt: datetime) -> None:
    """Проверить дату.

    Args:
        dt (datetime): дата

    Raises:
        ValidationError: ошибка
    """
    if dt < datetime.now(timezone.utc).date():
        raise ValidationError(_('Date cannot be less than current'))


def check_positive(number: int) -> None:
    """Проверить, что число положительное.

    Args:
        number (int): число

    Raises:
        ValidationError: ошибка
    """
    if number < 0:
        raise ValidationError(_('value has to be greater than zero'))


RESERVE_EXIST = 'Бронь на дату в промежутке уже существует'
ROOM_NOT_EXIST = 'Данной комнаты не существует'
DATE_END_ERROR = 'Дата окончания брони не может быть раньше старта брони'
DATE_EQUALLY = 'Забронировать можно минимум на один день'


def msg_error_reserve(data: dict) -> list[str]:
    """Получить сообщение ошибки бронирования.

    Args:
        data (dict): словарь с данными о бронировании

    Returns:
        list[str]: словарь с сообщениями об ошибках
    """
    start_date = data['start_date']
    end_date = data['end_date']
    reserve_id = data['reserve']
    msg = []

    if end_date < start_date:
        msg.append(DATE_END_ERROR)
    if end_date == start_date:
        msg.append(DATE_EQUALLY)
    try:
        room = Room.objects.get(id=data['room'])
    except Exception:
        msg.append(ROOM_NOT_EXIST)

    if Reserve.objects.filter(~Q(id=reserve_id), room=room, start_date__lte=start_date, end_date__gte=end_date)\
        or Reserve.objects.filter(~Q(id=reserve_id), room=room, start_date__gte=start_date, start_date__lte=end_date)\
            or Reserve.objects.filter(~Q(id=reserve_id), room=room, end_date__gte=start_date, end_date__lte=end_date):
        msg.append(RESERVE_EXIST)

    return msg


def validate_reserve(data: dict) -> None:
    """Проверка бронирования.

    Args:
        data (dict): словарь с данными о бронировании

    Raises:
        ValidationError: ошибка
    """
    msg_error = msg_error_reserve(data)
    if msg_error:
        raise ValidationError(msg_error[0])


class UUIDMixin(models.Model):
    """Класс, для добаления id."""

    id = models.UUIDField(primary_key=True, blank=True, editable=False, default=uuid4)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    """Класс, для добавления даты создания."""

    created = models.DateTimeField(
        _('created'),
        null=True, blank=True,
        default=get_datetime,
        validators=[check_created, ]
    )

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    """Класс, для добавления даты обновления."""

    modified = models.DateTimeField(
        _('modified'),
        null=True, blank=True,
        auto_now=True,
        validators=[check_modified]
    )

    class Meta:
        abstract = True


class Address(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель для адресса."""

    city = models.TextField(max_length=ADDRESS_MAX_LENGTH, null=False, blank=False)
    street = models.TextField(max_length=ADDRESS_MAX_LENGTH, null=False, blank=False)
    number = models.IntegerField(null=False, blank=False, validators=[check_positive])

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return f'{self.city}/{self.street}/{self.number}'

    class Meta:
        db_table = '"hotel"."address"'
        verbose_name = _('address')
        verbose_name_plural = _('address')


class HotelManager(models.Manager):
    """Менеджер для отеля."""

    def create(self, **kwargs: Any) -> Any:
        """Создать.

        Args:
            kwargs (Any): аргументы

        Raises:
            ValidationError: ошибка

        Returns:
            Any: экземпляр класса
        """
        if 'rating' in kwargs.keys():
            check_positive(kwargs['rating'])
            if (kwargs['rating']) > 5:
                raise ValidationError(_('value should not be more than five'))
        return super().create(**kwargs)


class Hotel(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель отеля."""

    name = models.TextField(_('name'), null=False, blank=False, max_length=NAMES_MAX_LENGTH)
    hotel_address = models.ForeignKey(Address, verbose_name='address', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.DecimalField(
        _('rating'), decimal_places=1,
        max_digits=2, validators=[MaxValueValidator(5), MinValueValidator(0)],
        default=0,
    )
    image = models.TextField(_('image'), null=True, blank=True, max_length=IMAGE_MAX_LENGTH)

    services = models.ManyToManyField(
        'Service', through='HotelService', verbose_name=_('services')
    )
    objects = HotelManager()

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return f'{self.name}: {self.rating}'

    class Meta:
        db_table = '"hotel"."hotel"'
        ordering = ['name', 'rating']
        verbose_name = _('hotel')
        verbose_name_plural = _('hotels')


class Service(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель сервиса."""

    name = models.TextField(_('name'), null=False, blank=False, max_length=NAMES_MAX_LENGTH)

    hotels = models.ManyToManyField(Hotel, through='HotelService', verbose_name=_('hotels'))
    reserves = models.ManyToManyField('Reserve', through='ReserveService', verbose_name=_('reserves'))

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return self.name

    class Meta:
        db_table = '"hotel"."service"'
        ordering = ['name']
        verbose_name = _('service')
        verbose_name_plural = _('services')


class HotelServiceManager(models.Manager):
    """Менеджер для отель-сервис."""

    def create(self, **kwargs: Any) -> Any:
        """Создать.

        Args:
            kwargs (Any): аргументы

        Returns:
            Any: экземпляр класса
        """
        if 'cost' in kwargs.keys():
            check_positive(kwargs['cost'])
        return super().create(**kwargs)


class HotelService(UUIDMixin, CreatedMixin):
    """Модель отель-сервис."""

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name=_('hotel'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name=_('service'))
    description = models.TextField(_('description'), null=True, blank=True, max_length=DESCRIPTION_MAX_LENGTH)
    cost = models.DecimalField(
        _('cost'), null=True, blank=True,
        default=0, validators=[MinValueValidator(0)],
        max_digits=11, decimal_places=2
    )

    objects = HotelServiceManager()

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return f'{self.hotel.name} - {self.service} {self.cost}'

    class Meta:
        db_table = '"hotel"."hotel_service"'
        unique_together = (('hotel', 'service'),)
        verbose_name = _('Relationship hotel service')
        verbose_name_plural = _('Relationships hotel service')


class_types = (
    ('apartment', _('apartment')),
    ('business', _('business')),
    ('de luxe', _('de luxe')),
    ('duplex', _('duplex')),
    ('standart', _('standart')),
    ('studio', _('studio')),
    ('suite', _('suite')),
    ('family', _('family')),
    ('single', _('single')),
    ('double', _('double')),
)


class RoomManager(models.Manager):
    """Менеджер для номера."""

    def create(self, **kwargs: Any) -> Any:
        """Создать.

        Args:
            kwargs (Any): аргументы

        Raises:
            ValidationError: ошибка

        Returns:
            Any: экземпляр класса
        """
        if 'number' in kwargs.keys():
            check_positive(kwargs['number'])
        if 'cost' in kwargs.keys():
            check_positive(kwargs['cost'])
        if 'category' in kwargs.keys():
            if not any([category[0] == kwargs['category'] for category in class_types]):
                raise ValidationError(f"category {kwargs['category']} is unknown")
        return super().create(**kwargs)


class Room(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель номер."""

    category = models.TextField(_('category'), null=False, blank=False, choices=class_types)
    floor = models.IntegerField(_('floor'), null=True, blank=True)
    number = models.IntegerField(_('number'), null=True, blank=True, validators=[MinValueValidator(0)])
    cost = models.DecimalField(
        _('cost'), null=True, blank=True,
        default=0, validators=[MinValueValidator(0)],
        max_digits=11, decimal_places=2
    )
    image = models.TextField(_('image'), null=True, blank=True, max_length=IMAGE_MAX_LENGTH)

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name=_('hotel'))
    clients = models.ManyToManyField('Client', through='Reserve', verbose_name=_('clients'))
    objects = RoomManager()

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return f'{self.category}, этаж: {self.floor}, номер: {self.number}'

    class Meta:
        db_table = '"hotel"."room"'
        ordering = ['category', 'floor']
        verbose_name = _('room')
        verbose_name_plural = _('rooms')


class ClientManager(models.Manager):
    """Менеджер для клиента."""

    def create(self, **kwargs: Any) -> Any:
        """Создать.

        Args:
            kwargs (Any): аргументы

        Returns:
            Any: экземпляр класса
        """
        if 'money' in kwargs.keys():
            check_positive(kwargs['money'])
        return super().create(**kwargs)


class Client(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель клиента."""

    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    money = models.DecimalField(
        _('money'), default=0,
        null=True, blank=True,
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    rooms = models.ManyToManyField(Room, through='Reserve', verbose_name=_('rooms'))
    objects = ClientManager()

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return f'{self.user.username} ({self.user.first_name} {self.user.last_name})'

    class Meta:
        db_table = '"hotel"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')


class ReserveManager(models.Manager):
    """Менеджер для бронирования."""

    def create(self, **kwargs: Any) -> Any:
        """Создать.

        Args:
            kwargs (Any): аргументы

        Returns:
            Any: экземпляр класса
        """
        if 'price' in kwargs.keys():
            check_positive(kwargs['price'])
        return super().create(**kwargs)


class Reserve(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель бронирование."""

    user = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_('reserved_user'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_('room'), related_name=_('room'))
    start_date = models.DateField(_('Date, from'), validators=[check_date, ])
    end_date = models.DateField(_('Date, until'), validators=[check_date, ])
    price = models.DecimalField(
        _('price'), null=True, blank=True,
        default=0, validators=[MinValueValidator(0)],
        max_digits=11, decimal_places=2
    )
    services = models.ManyToManyField(Service, through='ReserveService', verbose_name=_('services'))

    objects = ReserveManager()

    def __str__(self) -> str:
        """Метод строкового представления.

        Returns:
            str: строка
        """
        return f'{self.room.hotel.name} {self.room.number} {self.end_date}'

    class Meta:
        db_table = '"hotel"."reserve"'
        verbose_name = _('reserve')
        verbose_name_plural = _('reserves')

    def get_price(self) -> float:
        """Получить цену.

        Returns:
            float: цена
        """
        return (self.end_date - self.start_date).days * self.room.cost

    def clean(self):
        """Чистка."""
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'room': self.room.id,
            'reserve': self.id
        }
        validate_reserve(data)

    def save(self, *args, **kwargs) -> Any:
        """Сохранить.

        Args:
            args (Any): аргументы
            kwargs (Any): аргументы

        Returns:
            Any: сохранить
        """
        self.full_clean()
        if not self.price:
            self.price = self.get_price()
        return super().save(*args, **kwargs)


class ReserveService(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Модель бронирование-сервис."""

    reserve = models.ForeignKey(Reserve, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        db_table = '"hotel"."reserve_service"'
        unique_together = (('reserve', 'service'),)
        verbose_name = _('Relationship reserve service')
        verbose_name_plural = _('Relationships reserve service')
