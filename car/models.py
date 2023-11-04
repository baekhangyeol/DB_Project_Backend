from django.db import models

from employee.models import Branch


class CarType(models.Model):
    brand = models.CharField(max_length=100, verbose_name='차량 브랜드')
    SIZE_CHOICES = {
        ('small', '소형'),
        ('medium', '중형'),
        ('large', '대형'),
    }
    size = models.CharField(max_length=6, choices=SIZE_CHOICES, verbose_name='차량 크기')

    class Meta:
        verbose_name = '차량 유형'


class CarOption(models.Model):
    airconditioner = models.BooleanField(default=False)
    heatedseat = models.BooleanField(default=False)
    sunroof = models.BooleanField(default=False)
    navigation = models.BooleanField(default=False)
    blackbox = models.BooleanField(default=False)

    class Meta:
        verbose_name = '차량 옵션'


class Car(models.Model):
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='cars', on_delete=models.CASCADE, null=True)
    mileage = models.FloatField(default=0.0)
    availability = models.BooleanField(default=True)
    rental_price = models.IntegerField(default=0)
    options = models.ForeignKey(CarOption, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '차량'


class CarMaintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenances')
    maintenance_date = models.DateField()
    reason = models.TextField()
    cost = models.FloatField()

    class Meta:
        verbose_name = '정비'
