from django.db import models
from django.utils import timezone

from car.models import Car


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    driver_license_number = models.CharField(max_length=50)
    join_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = '고객'


class Rental(models.Model):
    RENTAL_STATUS_CHOICES = [
        ('reserved', '예약'),
        ('in_progress', '진행 중'),
        ('completed', '종료')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='rentals')
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, related_name='rentals')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_amount = models.IntegerField()
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=RENTAL_STATUS_CHOICES, default='reserved')

    class Meta:
        verbose_name = '대여'
