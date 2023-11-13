from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

@swagger_auto_schema(method='get', operation_summary='고객 정보 리스트와 현재 대여 중인 차량 정보를 조회한다.')
@api_view(['GET'])
def get_customers_with_rentals(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT customer.id, customer.name, customer.phone_number, customer.email,
                       car_car.id, car_cartype.brand, car_cartype.size, rental.start_date, rental.end_date
                FROM customer_customer AS customer
                LEFT JOIN customer_rental AS rental ON customer.id = rental.customer_id AND (rental.status = 'in_progress' OR rental.status = 'reserved')
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
