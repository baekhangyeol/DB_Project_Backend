from django.db import transaction
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.db import connection


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
            wage_insert_query = """
                INSERT INTO employee_wage (bank_account, amount)
                VALUES (%s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(wage_insert_query, [wage_data['bank_account'], wage_data['amount']])

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

            employee = Employee.objects.get(pk=employee_id)
            employee_serializer = EmployeeSerializer(employee)

            return JsonResponse(employee_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put', request_body=EmployeeSerializer, operation_summary='기존 직원 정보를 수정한다.')
@transaction.atomic
@api_view(['PUT'])
def update_employee(request, pk):

    employee_data = request.data
    wage_data = employee_data.pop('bank_account', None)
    branch_id = employee_data.pop('branch', None)

    with connection.cursor() as cursor:
        if branch_id is not None:
            cursor.execute('SELECT id FROM employee_branch WHERE id = %s', [branch_id])
            if not cursor.fetchone():
                return JsonResponse({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute('UPDATE employee_employee SET branch_id = %s WHERE id = %s', [branch_id, pk])

        if employee_data:
            update_statements = ', '.join([f"{key} = %s" for key in employee_data.keys()])
            update_values = list(employee_data.values()) + [pk]
            cursor.execute(f'UPDATE employee_employee SET {update_statements} WHERE id = %s', update_values)

        if wage_data:
            wage_data.pop('bank_account', None)
            update_wage_statements = ', '.join([f"{key} = %s" for key in wage_data.keys()])
            update_wage_values = list(wage_data.values())
            cursor.execute(
                f'UPDATE employee_wage SET {update_wage_statements} WHERE bank_account = (SELECT bank_account_id FROM employee_employee WHERE id = %s)',
                update_wage_values + [pk])

    try:
        updated_employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    employee_serializer = EmployeeSerializer(updated_employee)
    return JsonResponse(employee_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='delete', operation_summary='직원 삭제')
@transaction.atomic
@api_view(['DELETE'])
def delete_employee(request, pk):
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute('SELECT bank_account_id FROM employee_employee WHERE id = %s', [pk])
        result = cursor.fetchone()

        if result is None:
            return JsonResponse({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        bank_account_id = result[0]

        cursor.execute('DELETE FROM employee_employee WHERE id = %s', [pk])

        cursor.execute('DELETE FROM employee_wage WHERE bank_account = %s', [bank_account_id])

    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='post', request_body=BranchSerializer, operation_summary='지점 추가')
@transaction.atomic()
@api_view(['POST'])
def add_branch(request):
    if request.method == 'POST':
        branch_data = request.data

        try:
            branch_insert_query = """
                INSERT INTO employee_branch (branch_phone_number, address)
                VALUES (%s, %s)
            """

            with connection.cursor() as cursor:
                cursor.execute(branch_insert_query, [branch_data['branch_phone_number'], branch_data['address']])
                cursor.execute("SELECT LAST_INSERT_ID()")
                branch_id = cursor.fetchone()[0]

            branch = Branch.objects.get(pk=branch_id)
            branch_serializer = BranchSerializer(branch)

            return JsonResponse(branch_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put', request_body=BranchSerializer, operation_summary='지점 정보 수정')
@transaction.atomic()
@api_view(['PUT'])
def update_branch(request, pk):
    branch_data = request.data

    with connection.cursor() as cursor:
        update_statements = ', '.join([f"{key} = %s" for key in branch_data.keys()])
        update_values = list(branch_data.values()) + [pk]
        cursor.execute(f'UPDATE employee_branch SET {update_statements} WHERE id = %s', update_values)

    try:
        updated_branch = Branch.objects.get(pk=pk)
    except Branch.DoesNotExist:
        return JsonResponse({'error': '지점을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    branch_serializer = BranchSerializer(updated_branch)
    return JsonResponse(branch_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='delete', operation_summary='지점 정보 삭제')
@transaction.atomic()
@api_view(['DELETE'])
def delete_branch(request, pk):
    with connection.cursor() as cursor:
        cursor.execute('SELECT id FROM employee_branch WHERE id = %s', [pk])
        result = cursor.fetchone()

        if result is None:
            return JsonResponse({'error': '지점을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        cursor.execute('DELETE FROM employee_branch WHERE id = %s', [pk])

    return Response(status=status.HTTP_204_NO_CONTENT)