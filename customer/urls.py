from django.urls import path
from .views import *

urlpatterns = [
    path('', get_customers, name='get_customers_list'),
    path('add', add_customers, name='add_customer'),
    path('<int:pk>', update_customer, name='update_customer'),
    path('delete/<int:pk>', delete_customer, name='delete_customer'),
    path('detail/<int:pk>', get_customer, name='get-customer')
]
