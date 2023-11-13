from django.urls import path
from .views import *

urlpatterns = [
    path('add', add_employee, name='add-employee'),
    path('update/<int:pk>', update_employee, name='update-employee'),
    path('delete/<int:pk>', delete_employee, name='delete-employee'),
    path('branch/add', add_branch, name='add-branch'),
    path('branch/update/<int:pk>', update_branch, name='update-branch'),
    path('branch/delete/<int:pk>', delete_branch, name='delete-branch'),
    path('branch/', get_branch_list, name='branch-list'),
    path('branch/<int:pk>', get_branch_details, name='branch-detail')
]