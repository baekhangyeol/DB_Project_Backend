from django.db import transaction, IntegrityError
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
def add_employee(request, branch_id):
    if request.method == 'POST':
        wage_data = request.data.get('wage')
        employee_data = {
            'branch': branch_id,
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
                INSERT INTO employee_employee (branch_id, name, position, phone_number, email, wage_id)
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


@swagger_auto_schema(method='patch', request_body=EmployeeSerializer, operation_summary='기존 직원 정보를 수정한다.')
@transaction.atomic
@api_view(['PATCH'])
def update_employee(request, pk):
    employee_data = request.data
    wage_data = employee_data.pop('wage', None)
    branch_id = employee_data.pop('branch', None)

    try:
        updated_employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        if branch_id is not None:
            try:
                branch = Branch.objects.get(pk=branch_id)
                updated_employee.branch = branch
                updated_employee.save()
            except Branch.DoesNotExist:
                return JsonResponse({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

        if employee_data:
            for key, value in employee_data.items():
                setattr(updated_employee, key, value)
            updated_employee.save()

        if wage_data:
            existing_wage = updated_employee.wage
            if existing_wage:
                existing_wage.bank_account = wage_data.get('bank_account', existing_wage.bank_account)
                existing_wage.amount = wage_data.get('amount', existing_wage.amount)
                existing_wage.save()
            else:
                new_wage = Wage.objects.create(bank_account=wage_data['bank_account'], amount=wage_data['amount'])
                updated_employee.wage = new_wage

    updated_employee.refresh_from_db()
    employee_serializer = EmployeeSerializer(updated_employee)
    return JsonResponse(employee_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='delete', operation_summary='직원 삭제')
@transaction.atomic
@api_view(['DELETE'])
def delete_employee(request, pk):
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute('SELECT wage_id FROM employee_employee WHERE id = %s', [pk])
        result = cursor.fetchone()

        if result is None:
            return JsonResponse({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        wage_id = result[0]

        cursor.execute('DELETE FROM employee_employee WHERE id = %s', [pk])

        cursor.execute('DELETE FROM employee_wage WHERE bank_account = %s', [wage_id])

    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', operation_summary='직원의 상세 정보를 조회한다.')
@transaction.atomic()
@api_view(['GET'])
def get_employee(request, pk):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT employee.name, employee.position, employee.phone_number, employee.email,
                       branch.name, branch.branch_phone_number, branch.address,
                       wage.bank_account, wage.amount
                FROM employee_employee AS employee
                LEFT JOIN employee_branch AS branch ON employee.branch_id = branch.id
                LEFT JOIN employee_wage AS wage ON employee.wage_id = wage.bank_account
                WHERE employee.id = %s
            """, [pk])
            row = cursor.fetchone()

        if not row:
            return JsonResponse({'error': 'Employee not found'}, status=404)

        employee_data = {
            'name': row[0],
            'position': row[1],
            'phone_number': row[2],
            'email': row[3],
            'branch': {
                'branch_name': row[4],
                'branch_phone_number': row[5],
                'branch_address': row[6]
            },
            'wage': {
                'bank_account': row[7],
                'amount': row[8]
            }
        }

        return JsonResponse(employee_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@swagger_auto_schema(method='post', request_body=BranchSerializer, operation_summary='지점 추가')
@transaction.atomic()
@api_view(['POST'])
def add_branch(request):
    if request.method == 'POST':
        branch_data = request.data

        try:
            branch_insert_query = """
                INSERT INTO employee_branch (name, branch_phone_number, address)
                VALUES (%s, %s, %s)
            """

            with connection.cursor() as cursor:
                cursor.execute(branch_insert_query, [branch_data['name'], branch_data['branch_phone_number'], branch_data['address']])
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

        employee_count = Employee.objects.filter(branch_id=pk).count()
        if employee_count > 0:
            return JsonResponse({'error': '지점에 등록된 직원이 있어서 삭제할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        cursor.execute('DELETE FROM employee_branch WHERE id = %s', [pk])

    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', operation_summary='모든 지점을 조회한다.')
@api_view(['GET'])
def get_branch_list(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, branch_phone_number, address FROM employee_branch")
            branches = cursor.fetchall()

        branch_list = []
        for branch in branches:
            branch_dict = {
                'id': branch[0],
                'name': branch[1],
                'branch_phone_number': branch[2],
                'address': branch[3]
            }
            branch_list.append(branch_dict)

        return Response(branch_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='get', operation_summary='특정 지점의 상세 정보를 조회한다.')
@api_view(['GET'])
def get_branch_details(request, pk):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, branch_phone_number, address FROM employee_branch WHERE id = %s", [pk])
            branch = cursor.fetchone()

            if not branch:
                return Response({'message': '지점을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute("""
                SELECT id, name, position
                FROM employee_employee 
                WHERE branch_id = %s
            """, [pk])
            employees = cursor.fetchall()

            cursor.execute("""
                SELECT car.id, car_type.brand, car_type.size, car.availability
                FROM car_car as car
                INNER JOIN car_cartype as car_type ON car.car_type_id = car_type.id
                WHERE car.branch_id = %s
            """, [pk])
            cars = cursor.fetchall()

            employees_list = [{'employee_id': emp[0], 'name': emp[1], 'position': emp[2]} for emp in employees]

            cars_list = [{
                'car_id': car[0],
                'brand': car[1],
                'size': car[2],
                'availability': car[3],
            } for car in cars]

            branch_details = {
                'branch_id': branch[0],
                'name': branch[1],
                'branch_phone_number': branch[2],
                'address': branch[3],
                'employees': employees_list,
                'cars': cars_list
            }

        return Response(branch_details, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


