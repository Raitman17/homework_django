"""Модуль для сериализаторов."""

from rest_framework import serializers

from .models import Hotel, Reserve, Room, Service


class HotelSerializer(serializers.HyperlinkedModelSerializer):
    """Отель сериализатор."""

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'address',
            'rating', 'created', 'modified',
        ]


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    """Сервис сериализатор."""

    class Meta:
        model = Service
        fields = [
            'id', 'name',
            'created', 'modified',
        ]


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    """Номер сериализатор."""

    class Meta:
        model = Room
        fields = [
            'id', 'category', 'floor', 'number', 'cost',
            'hotel', 'created', 'modified',
        ]


class ReserveSerializer(serializers.ModelSerializer):
    """Бронирование сериализатор."""

    class Meta:
        model = Reserve
        fields = ('id', 'room', 'user', 'start_date', 'end_date')
        read_only = True
