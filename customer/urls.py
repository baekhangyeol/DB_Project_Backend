from django.urls import path
from .views import *

urlpatterns = [
    path('', get_customers_with_rentals, name='get_customers_list'),
    path('<int:pk>', update_customer, name='update_customer'),
    path('delete/<int:pk>', delete_customer, name='delete_customer'),
]
