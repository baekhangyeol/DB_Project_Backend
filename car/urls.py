from django.urls import path
from .views import create_car

urlpatterns = [
    path('cars/', create_car, name='create-car'),
]
