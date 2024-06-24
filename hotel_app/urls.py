"""Модуль для ссылок."""

from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'hotels', views.HotelViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'reserve', views.ReserveViewSet)

urlpatterns = [
    path('rest/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', views.HotelListView.as_view(), name='homepage'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('hotel/', views.hotel, name='hotel'),
    path('room/', views.room, name='room'),
    path('reserve/', views.reserve, name='reserve'),
    path('delete_reserve/', views.delete_reserve, name='delete_reserve'),
    path('book_by_date/', views.book_by_date, name='book_by_date')
]
