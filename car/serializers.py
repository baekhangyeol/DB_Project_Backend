from rest_framework import serializers
from .models import Car, CarType, CarOption, CarMaintenance


class CarMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMaintenance
        fields = '__all__'

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
        fields = ['id', 'car_type', 'mileage', 'availability', 'rental_price', 'options']

    def create(self, validated_data):
        car_type_data = validated_data.pop('car_type')
        options_data = validated_data.pop('options')
        car_type = CarType.objects.create(**car_type_data)
        options = CarOption.objects.create(**options_data)
        car = Car.objects.create(car_type=car_type, options=options, **validated_data)
        return car

    def update(self, instance, validated_data):
        car_type_data = validated_data.pop('car_type', None)
        options_data = validated_data.pop('options', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if car_type_data is not None:
            car_type_serializer = CarTypeSerializer(instance.car_type, data=car_type_data, partial=True)
            if car_type_serializer.is_valid():
                car_type_serializer.save()

        if options_data is not None:
            options_serializer = CarOptionSerializer(instance.options, data=options_data, partial=True)
            if options_serializer.is_valid():
                options_serializer.save()

        return instance
