"""Модуль для просмотра страниц."""

from typing import Any

from django.contrib.auth import decorators
from django.core import exceptions
from django.core import paginator as django_paginator
from django.shortcuts import redirect, render
from django.views.generic import ListView
from rest_framework import authentication, permissions, viewsets

from .forms import AddFundsForm, BookRoom, RegistrationForm
from .models import (Client, Hotel, HotelService, Reserve, ReserveService,
                     Room, Service, check_date, msg_error_reserve)
from .serializers import (HotelSerializer, ReserveSerializer, RoomSerializer,
                          ServiceSerializer)


class MyPermission(permissions.BasePermission):
    """Класс доступа."""

    def has_permission(self, request, _):
        """Разрешения.

        Args:
            request (_type_): запрос
            _ (_type_): _description_

        Returns:
            _type_: истина/ложь
        """
        if request.method in ('GET', 'OPTIONS', 'HEAD'):
            return bool(request.user and request.user.is_authenticated)
        elif request.method in ('POST', 'DELETE', 'PUT'):
            return bool(request.user and request.user.is_superuser)
        return False


def create_viewset(model_class, serializer):
    """Создать просмотр модели.

    Args:
        model_class (_type_): класс модели
        serializer (_type_): сериализатор

    Returns:
        _type_: набор моделей
    """
    class ViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer
        authentication_classes = [authentication.TokenAuthentication]
        permission_classes = [MyPermission]

    return ViewSet


HotelViewSet = create_viewset(Hotel, HotelSerializer)
ServiceViewSet = create_viewset(Service, ServiceSerializer)
RoomViewSet = create_viewset(Room, RoomSerializer)
ReserveViewSet = create_viewset(Reserve, ReserveSerializer)


class HotelListView(ListView):
    """Просмотр списка отелей."""

    model = Hotel
    template_name = 'index.html'
    paginate_by = 10
    context_object_name = 'hotels'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """получить контекстные данные.

        Returns:
            dict[str, Any]: контекст

        Args:
            kwargs (Any): аргументы
        """
        context = super().get_context_data(**kwargs)
        instances = Hotel.objects.all()
        paginator = django_paginator.Paginator(instances, 10)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)
        context['hotels_list'] = page_obj
        return context


def register(request):
    """Регистрация.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    errors = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(user=user)
            return redirect('homepage')
        else:
            errors = form.errors
    else:
        form = RegistrationForm()
    return render(
        request,
        'registration/register.html',
        {'form': form, 'errors': errors},
    )


def hotel(request):
    """Отель.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    id_ = request.GET.get('id', None)
    if not id_:
        return redirect('homepage')
    try:
        hotel = Hotel.objects.get(id=id_) if id_ else None
        rooms = Room.objects.filter(hotel=id_) if id_ else None
    except exceptions.ValidationError:
        return redirect('homepage')
    context = {'hotel': hotel, 'rooms': rooms}
    return render(
        request,
        'hotel.html',
        context
    )


def room(request):
    """Номер.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    id_ = request.GET.get('id', None)
    if not id_:
        return redirect('homepage')
    try:
        room = Room.objects.get(id=id_)
    except exceptions.ValidationError:
        return redirect('homepage')
    context = {'room': room}
    return render(
        request,
        'room.html',
        context
    )


def delete_reserve(request):
    """Удалить бронирование.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    client = Client.objects.get(user=request.user)
    id_ = request.GET.get('id', None)
    try:
        reserve = Reserve.objects.get(id=id_)
    except exceptions.ValidationError:
        return redirect('homepage')
    reserve.delete()
    client.money += reserve.price
    client.save()
    return redirect('profile')


@decorators.login_required
def profile(request):
    """Профиль.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    client = Client.objects.get(user=request.user)
    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            money = form.cleaned_data.get('money')
            client.money += money
            client.save()
    else:
        form = AddFundsForm()

    return render(
        request,
        'profile.html',
        {
            'form': form,
            'client_data': {'username': client.user.username, 'money': client.money},
            'reserve': Reserve.objects.filter(user=client)
        }
    )


def check_reserve(data: dict) -> list[str]:
    """Проверить бронирование.

    Args:
        data (dict): словарь с данными о бронировании

    Returns:
        list[str]: список с сообщениями об ошибках
    """
    msg = []
    try:
        check_date(data['start_date'])
        check_date(data['end_date'])
    except exceptions.ValidationError:
        msg.append('Дата должна быть больше текущей!')

    msg_error = msg_error_reserve(data)
    if msg_error:
        msg += msg_error

    return msg


@decorators.login_required
def reserve(request):
    """Бронирование.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    room_id = request.GET.get('id', None)
    try:
        room = Room.objects.get(id=room_id)
    except exceptions.ValidationError:
        return redirect('homepage')
    except Room.DoesNotExist:
        return redirect('homepage')
    reserve_room = Reserve.objects.filter(room=room)
    client = Client.objects.get(user=request.user)
    form_errors = []
    services = room.hotel.services.all()
    if request.method == 'POST':
        form = BookRoom(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            reserve = Reserve(user=client, room=room, start_date=start_date, end_date=end_date)

            data = {
                'start_date': start_date,
                'end_date': end_date,
                'room': room_id,
                'reserve': reserve.id,
            }
            form_errors += check_reserve(data)

            price = reserve.get_price()
            service_reserve = []
            for service in services:
                value = request.POST.get(service.name)
                if value:
                    service_cost = HotelService.objects.get(hotel=room.hotel, service=service).cost
                    price += service_cost * (end_date - start_date).days
                    service_reserve.append(ReserveService(reserve=reserve, service=service))

            reserve.price = price
            if client.money < reserve.price:
                form_errors.append(f'Недостаточно средств! текущая цена:{reserve.price} у вас на счету: {client.money}')
            if not form_errors:
                client.money -= reserve.price
                client.save()
                reserve.save()
                for service in service_reserve:
                    service.save()
                return redirect('profile')
    else:
        form = BookRoom()

    return render(
        request,
        'reserve.html',
        {
            'form': form,
            'room': room,
            'room_id': room_id,
            'form_errors': form_errors,
            'services': services,
            'reserve_room': reserve_room
        }
    )


def book_by_date(request):
    """Забронировать по дате.

    Args:
        request (_type_): запрос

    Returns:
        _type_: ответ
    """
    form_errors = []
    reserves = []
    free_rooms = None
    if request.method == 'POST':
        form = BookRoom(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            try:
                check_date(start_date)
                check_date(end_date)
            except exceptions.ValidationError:
                form_errors.append('Дата должна быть больше текущей!')
            reserves += Reserve.objects.filter(start_date__lte=start_date, end_date__gte=end_date)
            reserves += Reserve.objects.filter(start_date__gte=start_date, start_date__lte=end_date)
            reserves += Reserve.objects.filter(end_date__gte=start_date, end_date__lte=end_date)
            rooms = []
            for reserve in reserves:
                rooms.append(reserve.room.id)
            free_rooms = Room.objects.exclude(id__in=rooms) if rooms else Room.objects.all()

    else:
        form = BookRoom()

    return render(
        request,
        'book_by_date.html',
        {
            'form': form,
            'form_errors': form_errors,
            'rooms': free_rooms,
        }
    )
