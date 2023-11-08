from django.urls import path
from .views import *

urlpatterns = [
    path('add/', add_employee, name='add-employee'),
    path('update/<int:pk>', update_employee, name='update-employee'),
    path('delete/<int:pk>', delete_employee, name='delete-employee')
]