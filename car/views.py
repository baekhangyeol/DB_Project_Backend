from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Car
from .serializers import CarSerializer


@swagger_auto_schema(method='post', request_body=CarSerializer, operation_summary='새로운 차량을 등록한다.')
@api_view(['POST'])
def create_car(request):
    if request.method == 'POST':
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete', operation_summary='차량을 삭제한다.')
@api_view(['DELETE'])
def delete_car(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response({'message':'차량을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    car.delete()
    return Response({'message':'차량이 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)