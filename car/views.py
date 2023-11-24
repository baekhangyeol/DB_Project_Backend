from django.db import transaction, connection
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Car
from .serializers import CarSerializer


@swagger_auto_schema(method='post', request_body=CarSerializer, operation_summary='새로운 차량을 등록한다.')
@transaction.atomic
@api_view(['POST'])
def create_car(request, branch_id):
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
                    branch_id,
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
            return Response({'message': '잘못된 데이터 입력입니다.', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
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
def update_car(request, branch_id, pk):
    serializer = CarSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    update_fields = []
    options_update_fields = []
    type_update_fields = []

    car_options_data = validated_data.pop('options', None)
    car_type_data = validated_data.pop('car_type', None)

    if car_options_data:
        for field, value in car_options_data.items():
            options_update_fields.append(f"{field} = {'TRUE' if value else 'FALSE'}")

    if car_type_data:
        for field, value in car_type_data.items():
            type_update_fields.append(f"{field} = '{value}'")

    for field, value in validated_data.items():
        if isinstance(value, bool):
            update_fields.append(f"{field} = {'TRUE' if value else 'FALSE'}")
        elif isinstance(value, str):
            update_fields.append(f"{field} = '{value}'")
        elif isinstance(value, (int, float)):
            update_fields.append(f"{field} = {value}")

    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT options_id, car_type_id FROM car_car WHERE id = %s", [pk])
            result = cursor.fetchone()
            options_id = result[0]
            car_type_id = result[1]

            if options_update_fields and options_id:
                options_update_query = f"UPDATE car_caroption SET {', '.join(options_update_fields)} WHERE id = %s"
                cursor.execute(options_update_query, [options_id])

            if type_update_fields and car_type_id:
                type_update_query = f"UPDATE car_cartype SET {', '.join(type_update_fields)} WHERE id = %s"
                cursor.execute(type_update_query, [car_type_id])

            # Car 인스턴스 업데이트
            if update_fields:
                update_query = f"UPDATE car_car SET {', '.join(update_fields)} WHERE id = %s AND branch_id = %s"
                cursor.execute(update_query, [pk, branch_id])
                if cursor.rowcount == 0:
                    return Response({'message': '해당 지점에 차량을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': '차량 정보가 수정되었습니다.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


availability_parameter = openapi.Parameter(
    'availability', openapi.IN_QUERY,
    description="사용 가능 여부를 필터링합니다. 기본값은 True입니다.",
    type=openapi.TYPE_BOOLEAN,
    default=True
)


@swagger_auto_schema(method='get', operation_summary='렌트카 이용 현황을 조회한다.', manual_parameters=[availability_parameter])
@api_view(['GET'])
def get_available_cars(request):
    availability = request.query_params.get('availability', None)

    if availability is not None:
        availability = True if availability.lower() == 'true' else False

    query = """
        SELECT car_car.id, car_cartype.brand, car_cartype.size, car_car.availability,
        employee_branch.name
        FROM car_car
        INNER JOIN car_cartype ON car_car.car_type_id = car_cartype.id
        INNER JOIN car_caroption ON car_car.options_id = car_caroption.id
        INNER JOIN employee_branch ON car_car.branch_id = employee_branch.id
    """

    if availability is not None:
        query += " WHERE car_car.availability = %s"

    try:
        with connection.cursor() as cursor:
            if availability is not None:
                cursor.execute(query, [availability])
            else:
                cursor.execute(query)
            cars = cursor.fetchall()

        cars_list = []
        for car in cars:
            car_dict = {
                'id': car[0],
                'car_type': {
                    'brand': car[1],
                    'size': car[2],
                    'availability': car[3]
                },
                'branch_name': car[4]
            }
            cars_list.append(car_dict)

        return Response(cars_list, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@swagger_auto_schema(method='get', operation_summary='차량의 정비 이력을 조회한다.')
@api_view(['GET'])
def get_car_maintenance(request, pk):
    query = """
        SELECT id, car_id, maintenance_date, reason, cost 
        FROM car_carmaintenance 
        WHERE car_id = %s
        """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [pk])
            result = cursor.fetchall()

        if not result:
            return Response({'message': '해당 차량의 정비 이력이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        columns = [col[0] for col in cursor.description]
        maintenances = [
            dict(zip(columns, row))
            for row in result
        ]

        return Response(maintenances, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': '서버 에러 발생', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='get', operation_summary='차량의 상세 정보 및 정비 이력을 조회한다.')
@api_view(['GET'])
def get_car_details(request, pk):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT car_car.id, car_cartype.brand, car_cartype.size, car_car.mileage, car_car.rental_price, car_car.availability,
                car_caroption.airconditioner, car_caroption.heatedseat, car_caroption.sunroof, car_caroption.navigation, car_caroption.blackbox,
                employee_branch.name
                FROM car_car
                INNER JOIN car_cartype ON car_car.car_type_id = car_cartype.id
                INNER JOIN car_caroption ON car_car.options_id = car_caroption.id
                INNER JOIN employee_branch ON car_car.branch_id = employee_branch.id
                WHERE car_car.id = %s
            """, [pk])
            car = cursor.fetchone()

            if not car:
                return Response({'message': '차량을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

            car_details = {
                'id': car[0],
                'car_type': {
                    'brand': car[1],
                    'size': car[2],
                    'mileage': car[3],
                    'rental_price': car[4],
                    'availability': car[5],
                    'options': {
                        'airconditioner': car[6],
                        'heatedseat': car[7],
                        'sunroof': car[8],
                        'navigation': car[9],
                        'blackbox': car[10]
                    }
                },
                'branch_name': car[11]
            }

            cursor.execute("""
                SELECT id, maintenance_date, reason, cost
                FROM car_carmaintenance
                WHERE car_id = %s
            """, [pk])
            maintenances = cursor.fetchall()

            maintenance_list = [{
                'id': maintenance[0],
                'maintenance_date': maintenance[1],
                'reason': maintenance[2],
                'cost': maintenance[3]
            } for maintenance in maintenances]

            car_details['maintenances'] = maintenance_list

        return Response(car_details, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': '서버 에러 발생', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
