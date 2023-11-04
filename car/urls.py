from django.urls import path
from .views import *

urlpatterns = [
    path('create/', create_car, name='create_car'),
    path('delete/<int:pk>', delete_car, name='delete_car'),
    path('update/<int:pk>', update_car, name='update_car'),
]
