from rest_framework import serializers
from .models import Employee, Wage, Branch


class WageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wage
        fields = ['bank_account', 'amount']


class EmployeeSerializer(serializers.ModelSerializer):
    bank_account = WageSerializer()

    class Meta:
        model = Employee
        fields = ['branch', 'name', 'position', 'phone_number', 'email', 'bank_account']

    def create(self, validated_data):
        wage_data = validated_data.pop('bank_account')
        wage = Wage.objects.create(**wage_data)
        employee = Employee.objects.create(bank_account=wage, **validated_data)
        return employee


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
