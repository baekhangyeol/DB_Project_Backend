from django.db import transaction, connection
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer


@swagger_auto_schema(method='post', request_body=EmployeeSerializer, operation_summary='새로운 직원을 추가한다.')
@transaction.atomic
@api_view(['POST'])
def add_employee(request):
    if request.method == 'POST':
        wage_data = request.data.get('bank_account')
        employee_data = {
            'branch': request.data.get('branch'),
            'name': request.data.get('name'),
            'position': request.data.get('position'),
            'phone_number': request.data.get('phone_number'),
            'email': request.data.get('email'),
        }

        try:
            # Wage 객체를 먼저 생성
            wage_insert_query = """
                INSERT INTO employee_wage (bank_account, amount)
                VALUES (%s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(wage_insert_query, [wage_data['bank_account'], wage_data['amount']])

            # Employee 객체 생성
            employee_insert_query = """
                INSERT INTO employee_employee (branch_id, name, position, phone_number, email, bank_account_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(employee_insert_query, [
                    employee_data['branch'],
                    employee_data['name'],
                    employee_data['position'],
                    employee_data['phone_number'],
                    employee_data['email'],
                    wage_data['bank_account']
                ])
                cursor.execute("SELECT LAST_INSERT_ID()")
                employee_id = cursor.fetchone()[0]

            # 생성된 Employee 객체 가져오기
            employee = Employee.objects.get(pk=employee_id)
            employee_serializer = EmployeeSerializer(employee)

            return JsonResponse(employee_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)