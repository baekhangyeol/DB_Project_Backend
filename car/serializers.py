from rest_framework import serializers
from .models import Car, CarType, CarOption


class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = ['id', 'brand', 'size']


class CarOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarOption
        fields = ['id', 'airconditioner', 'heatedseat', 'sunroof', 'navigation', 'blackbox']


class CarSerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()
    options = CarOptionSerializer()

    class Meta:
        model = Car
        fields = ['id', 'car_type', 'branch', 'mileage', 'availability', 'rental_price', 'options']

    def create(self, validated_data):
        car_type_data = validated_data.pop('car_type')
        options_data = validated_data.pop('options')
        car_type = CarType.objects.create(**car_type_data)
        options = CarOption.objects.create(**options_data)
        car = Car.objects.create(car_type=car_type, options=options, **validated_data)
        return car
