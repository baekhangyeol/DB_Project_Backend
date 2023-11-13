from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from customer.serializers import CustomerSerializer


@swagger_auto_schema(method='get', operation_summary='고객 정보 리스트와 현재 대여 중인 차량 정보를 조회한다.')
@api_view(['GET'])
def get_customers_with_rentals(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT customer.id, customer.name, customer.phone_number, customer.email,
                       car_car.id, car_cartype.brand, car_cartype.size, rental.start_date, rental.end_date
                FROM customer_customer AS customer
                LEFT JOIN customer_rental AS rental ON customer.id = rental.customer_id AND rental.status = 'in_progress'
                LEFT JOIN car_car ON rental.car_id = car_car.id
                LEFT JOIN car_cartype ON car_car.car_type_id = car_cartype.id
            """)
            customers = cursor.fetchall()

        customer_list = []
        for customer in customers:
            rental_info = {
                'car_id': customer[4],
                'brand': customer[5],
                'size': customer[6],
                'start_date': customer[7],
                'end_date': customer[8]
            } if customer[4] else None

            customer_dict = {
                'id': customer[0],
                'name': customer[1],
                'phone_number': customer[2],
                'email': customer[3],
                'rental_car': rental_info
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
            cursor.execute("SELECT id FROM customer_rental WHERE customer_id = %s AND status IN ('reserved', 'in_progress')", [pk])
            if cursor.fetchone():
                return Response({'message': '차량 대여 중인 고객은 삭제할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # 고객 삭제
            cursor.execute("DELETE FROM customer_customer WHERE id = %s", [pk])
            if cursor.rowcount == 0:
                return Response({'message': '고객을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': '고객이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
