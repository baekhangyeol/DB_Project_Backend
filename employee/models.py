from django.db import models


class Branch(models.Model):
    name = models.TextField(null=True)
    branch_phone_number = models.CharField(max_length=15)
    address = models.TextField()

    class Meta:
        verbose_name = '지점'
        verbose_name_plural = '지점들'


class Wage(models.Model):
    bank_account = models.CharField(max_length=100,primary_key= True)
    amount = models.IntegerField()

    class Meta:
        verbose_name = '임금'

class Employee(models.Model):
    branch = models.ForeignKey(Branch, related_name='employees', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    wage = models.ForeignKey(Wage, related_name='employees', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = '직원'
