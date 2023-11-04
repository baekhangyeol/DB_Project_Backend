from django.db import transaction, connection
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Car
from .serializers import CarSerializer


@swagger_auto_schema(method='post', request_body=CarSerializer, operation_summary='새로운 차량을 등록한다.')
@transaction.atomic
@api_view(['POST'])
def create_car(request):
    if request.method == 'POST':
        data = request.data
        car_type_data = data.get('car_type', {})
        options_data = data.get('options', {})

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO car_caroption (airconditioner, heatedseat, sunroof, navigation, blackbox)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    options_data.get('airconditioner', False),
                    options_data.get('heatedseat', False),
                    options_data.get('sunroof', False),
                    options_data.get('navigation', False),
                    options_data.get('blackbox', False)
                ])
                car_option_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO car_cartype (brand, size)
                    VALUES (%s, %s)
                """, [
                    car_type_data.get('brand', ''),
                    car_type_data.get('size', '')
                ])
                car_type_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO car_car (car_type_id, branch_id, mileage, availability, rental_price, options_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    car_type_id,
                    data.get('branch', 0),
                    data.get('mileage', 0.0),
                    data.get('availability', True),
                    data.get('rental_price', 0),
                    car_option_id
                ])
                car_id = cursor.lastrowid

            car_instance = Car.objects.get(id=car_id)
            car_serializer = CarSerializer(car_instance)

            return Response(car_serializer.data, status=status.HTTP_201_CREATED)
        except KeyError as e:
            # 데이터가 잘못되었을 때의 에러 처리
            return Response({'message': '잘못된 데이터 입력입니다.', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 그 외의 예외 처리
            return Response({'message': '서버 에러 발생', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='delete', operation_summary='차량을 삭제한다.')
@transaction.atomic
@api_view(['DELETE'])
def delete_car(request, pk):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT options_id, car_type_id FROM car_car WHERE id = %s", [pk])
            car = cursor.fetchone()
            if not car:
                return Response({'message': '차량을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
            car_option_id, car_type_id = car

            cursor.execute("DELETE FROM car_car WHERE id = %s", [pk])

            cursor.execute("DELETE FROM car_caroption WHERE id = %s", [car_option_id])

            cursor.execute("DELETE FROM car_cartype WHERE id = %s", [car_type_id])

        return Response({'message': '차량이 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        transaction.rollback()
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='patch', request_body=CarSerializer, operation_summary='차량 정보를 수정한다.')
@api_view(['PATCH'])
@transaction.atomic
def update_car(request, pk):
    serializer = CarSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    update_fields = []

    for field, value in validated_data.items():
        if isinstance(value, bool):
            update_fields.append(f"{field} = {'TRUE' if value else 'FALSE'}")
        elif isinstance(value, str):
            update_fields.append(f"{field} = '{value}'")
        elif isinstance(value, (int, float)):
            update_fields.append(f"{field} = {value}")

    update_set = ', '.join(update_fields)
    query = f"UPDATE car_car SET {update_set} WHERE id = %s"

    with connection.cursor() as cursor:
        try:
            cursor.execute(query, [pk])
            if cursor.rowcount == 0:
                return Response({'message': '차량을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': '차량 정보가 수정되었습니다.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)