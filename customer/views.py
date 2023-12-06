from datetime import datetime

import status as status
from django.db import connection, IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from customer.models import Customer, Rental
from customer.serializers import CustomerSerializer, RentalSerializer


@swagger_auto_schema(method='post', request_body=CustomerSerializer, operation_summary="고객을 등록한다.")
@api_view(['POST'])
def add_customers(request):
    if request.method == 'POST':
        data = request.data

        name = data.get('name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        driver_license_number = data.get('driver_license_number')

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customer_customer (name, phone_number, email, driver_license_number, join_date) "
                "VALUES (%s, %s, %s, %s, NOW())",
                [name, phone_number, email, driver_license_number]
            )
            cursor.execute("SELECT LAST_INSERT_ID()")
            customer_id = cursor.fetchone()[0]

            customer = Customer.objects.get(pk=customer_id)
            customer_serializer = CustomerSerializer(customer)

        return JsonResponse(customer_serializer.data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(method='get', operation_summary='고객 정보 리스트를 출력한다.')
@api_view(['GET'])
def get_customers(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT customer.id, customer.name, customer.phone_number, customer.email
                FROM customer_customer AS customer
            """)
            customers = cursor.fetchall()

        customer_list = []
        for customer in customers:
            customer_dict = {
                'id': customer[0],
                'name': customer[1],
                'phone_number': customer[2],
                'email': customer[3]
            }
            customer_list.append(customer_dict)

        return Response(customer_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='patch', request_body=CustomerSerializer, operation_summary='특정 고객의 정보를 수정한다.')
@api_view(['PATCH'])
def update_customer(request, pk):
    try:
        with connection.cursor() as cursor:
            data = request.data
            update_fields = []

            for field, value in data.items():
                if isinstance(value, str):
                    update_fields.append(f"{field} = '{value}'")

            update_set = ', '.join(update_fields)
            cursor.execute(f"UPDATE customer_customer SET {update_set} WHERE id = %s", [pk])

            if cursor.rowcount == 0:
                return Response({'message': '고객을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': '고객 정보가 수정되었습니다.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete', operation_summary='특정 고객을 삭제한다.')
@api_view(['DELETE'])
def delete_customer(request, pk):
    try:
        with connection.cursor() as cursor:
            # 현재 대여 중인 차량이 있는지 확인
            cursor.execute("SELECT id, status FROM customer_rental WHERE customer_id = %s", [pk])
            rental_info = cursor.fetchone()

            if rental_info:
                rental_id, rental_status = rental_info
                if rental_status in ('reserved', 'in_progress'):
                    return Response({'message': '차량 대여 중인 고객은 삭제할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

                if rental_status == 'returned':
                    # customer_rental 테이블에서 해당 customer_id를 가진 레코드 삭제
                    cursor.execute("DELETE FROM customer_rental WHERE customer_id = %s", [pk])

                    try:
                        # customer_customer 테이블에서 해당 id를 가진 레코드 삭제
                        cursor.execute("DELETE FROM customer_customer WHERE id = %s", [pk])
                    except IntegrityError:
                        return Response({'message': '고객을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

                    return Response({'message': '고객이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'message': '고객 삭제는 \'returned\' 상태에서만 가능합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='get', operation_summary='고객의 상세 정보를 조회한다.')
@api_view(['GET'])
def get_customer(request, pk):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT customer.id, customer.name, customer.phone_number, customer.email,
                       customer.driver_license_number, customer.join_date,
                       rental.id, rental.start_date, rental.end_date, rental.total_amount, rental.payment_method, rental.status,
                       car.id, car_type.brand
                FROM customer_customer AS customer
                LEFT JOIN customer_rental AS rental ON customer.id = rental.customer_id
                LEFT JOIN car_car AS car ON rental.car_id = car.id
                LEFT JOIN car_cartype AS car_type ON car.car_type_id = car_type.id
                WHERE customer.id = %s
            """, [pk])
            rows = cursor.fetchall()

        if not rows:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        customer_data = {
            'id': rows[0][0],
            'name': rows[0][1],
            'phone_number': rows[0][2],
            'email': rows[0][3],
            'driver_license': rows[0][4],
            'join_date': rows[0][5],
            'rentals': []
        }

        for row in rows:
            if row[6]:
                rental_data = {
                    'rental_id': row[6],
                    'start_date': row[7],
                    'end_date': row[8],
                    'total_amount': row[9],
                    'payment_method': row[10],
                    'status': row[11],
                    'car': {
                        'car_id': row[12],
                        'brand': row[13]
                    }
                }
                customer_data['rentals'].append(rental_data)

        return JsonResponse(customer_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@swagger_auto_schema(method='patch', request_body=RentalSerializer, operation_summary='대여 정보를 수정한다.')
@api_view(['PATCH'])
def update_rental(request, rental_id):
    try:
        serializer = RentalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # status 필드 추출
        updated_status = serializer.validated_data.get('status')

        # 데이터베이스 업데이트
        Rental.objects.filter(id=rental_id).update(status=updated_status)

        # 업데이트된 레코드 정보 확인
        updated_rental = Rental.objects.get(id=rental_id)

        return Response({'status': updated_rental.status}, status=status.HTTP_200_OK)

    except Rental.DoesNotExist:
        return Response({'message': '대여 정보를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]