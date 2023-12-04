from rest_framework import serializers
from .models import Employee, Wage, Branch


class WageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wage
        fields = ['bank_account', 'amount']

class EmployeeSerializer(serializers.ModelSerializer):
    wage = WageSerializer()

    class Meta:
        model = Employee
        fields = ['name', 'position', 'phone_number', 'email', 'wage']

    def create(self, validated_data):
        wage_data = validated_data.pop('wage')
        try:
            existing_wage = Wage.objects.get(bank_account=wage_data['bank_account'])
            for key, value in wage_data.items():
                setattr(existing_wage, key, value)
            existing_wage.save()
        except Wage.DoesNotExist:
            existing_wage = Wage.objects.create(**wage_data)

        employee = Employee.objects.create(wage=existing_wage, **validated_data)
        return employee


class WageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wage
        fields = ['bank_account', 'amount']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
