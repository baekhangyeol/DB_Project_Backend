from django.db import models


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
    option_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = '차량 옵션'


class Car(models.Model):
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    mileage = models.FloatField(default=0.0)
    availability = models.BooleanField(default=True)
    rental_price = models.IntegerField(default=0)
    options = models.ForeignKey(CarOption, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '차량'
