from django.db import models


class Branch(models.Model):
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    class Meta:
        verbose_name = '지점'
        verbose_name_plural = '지점들'


class Employee(models.Model):
    branch = models.ForeignKey(Branch, related_name='employees', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    bank_account = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=0, default=30000000)