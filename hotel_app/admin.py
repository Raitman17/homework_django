"""Модуль для админки."""

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (Client, Hotel, HotelService, Reserve, ReserveService,
                     Room, Service, models)


class HotelAdminForm(forms.ModelForm):
    """Форма для отеля."""

    rating = forms.DecimalField(
        widget=forms.NumberInput(attrs={'min': 0.0, 'max': 5.0, 'step': 0.1}),
        label=_('rating')
    )

    class Meta:
        model = Hotel
        fields = '__all__'


class RoomAdminForm(forms.ModelForm):
    """Форма для номера."""

    number = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': 0, 'step': 1}),
        label=_('number')
    )
    cost = forms.DecimalField(
        widget=forms.NumberInput(attrs={'min': 0, 'step': 1}),
        label=_('cost')
    )

    class Meta:
        model = Room
        fields = '__all__'


class ClientAdminForm(forms.ModelForm):
    """Форма для клиента."""

    money = forms.DecimalField(
        widget=forms.NumberInput(attrs={'min': 0, 'step': 1}),
        label=_('money')
    )

    class Meta:
        model = Client
        fields = '__all__'


class HotelServiceInline(admin.TabularInline):
    """Встроенная строка для отеля-сервиса."""

    model = HotelService
    extra = 1


class RoomClientInline(admin.TabularInline):
    """Встроенная строка для номера-клиента."""

    model = Reserve
    extra = 1


class ReserveServiceInline(admin.TabularInline):
    """Встроенная строка для бронирования-сервиса."""

    model = ReserveService
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    """Администратор модели отель."""

    form = HotelAdminForm
    extra = 1
    inlines = (HotelServiceInline,)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Администратор модели сервис."""

    model = Service
    inlines = (HotelServiceInline,)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Администратор модели номер."""

    form = RoomAdminForm


@admin.register(HotelService)
class HotelServiceAdmin(admin.ModelAdmin):
    """Администратор модели отель-сервис."""

    model = HotelService


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Администратор модели клиент."""

    model = ClientAdminForm
    formfield_overrides = {
        models.DecimalField: {'widget': forms.NumberInput(attrs={'min': 0, 'step': 1})}
    }
    inlines = (RoomClientInline,)


@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    """Администратор модели бронирование."""

    model = Reserve
    inlines = (ReserveServiceInline,)


@admin.register(ReserveService)
class ReserveServiceAdmin(admin.ModelAdmin):
    """Администратор модели бронирование-сервис."""

    model = ReserveService
