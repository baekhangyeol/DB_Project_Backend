from rest_framework import serializers
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class RentalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rental
        fields = ['status']
