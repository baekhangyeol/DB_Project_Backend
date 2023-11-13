from django.urls import path
from .views import *

urlpatterns = [
    path('', get_customers_with_rentals, name='get_customers_list'),
]
