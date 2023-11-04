from django.urls import path
from .views import *

urlpatterns = [
    path('/create/', create_car, name='create_car'),
    path('/delete/<int:pk>', delete_car, name='delete_car'),
]
