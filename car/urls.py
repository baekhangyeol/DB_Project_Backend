from django.urls import path
from .views import *

urlpatterns = [
    path('create', create_car, name='create_car'),
    path('delete/<int:pk>', delete_car, name='delete_car'),
    path('update/<int:pk>', update_car, name='update_car'),
    path('', get_available_cars, name='get_car'),
    path('maintenance/<int:pk>', get_car_maintenance, name='get_maintenance')
]
