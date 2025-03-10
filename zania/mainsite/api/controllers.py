from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from utils.helpers.responses import SuccessResponse, ErrorResponse
from rest_framework import status
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from utils.views import CustomPaginator
import json
from rest_framework.throttling import AnonRateThrottle
from mainsite.models import Product,Order
from .serializers import OrderSerializer,ProductSerializer
from utils.helpers.permissions import ApiKeyPermission


paginator = CustomPaginator()

class ProductViewSetAPI(APIView):
    
    permission_classes = (ApiKeyPermission,)

    # throttle_classes = [AnonRateThrottle,]
    
    def get(self, request, version, format=None):
        try:
            product_data = Product.objects.all().values()
            paginated_products = paginator.paginate_queryset(product_data,request)
            paginated_response = paginator.get_paginated_response(paginated_products)
            return SuccessResponse(paginated_response.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return ErrorResponse(str(e),status=status.HTTP_400_BAD_REQUEST)
            

class OrderViewSetAPI(APIView):
    # permission_classes = (ApiKeyPermission)
    # throttle_classes = [AnonRateThrottle]
    def create(self, request):
        products_data = request.data.get("products", [])
        total_price = 0
        product_instances = []

        for item in products_data:
            try:
                product = Product.objects.get(id=item['id'])
                if product.stock < item['quantity']:
                    return ErrorResponse({"error": f"Insufficient stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)
                product.stock -= item['quantity']
                product_instances.append(product)
                total_price += product.price * item['quantity']
            except Product.DoesNotExist:
                return ErrorResponse({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        for product in product_instances:
            product.save()
        
        order = Order.objects.create(products=products_data, total_price=total_price, status='pending')
        return SuccessResponse(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
