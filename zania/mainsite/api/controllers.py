from rest_framework.views import APIView
from utils.helpers.responses import SuccessResponse, ErrorResponse
from rest_framework import status
from utils.views import CustomPaginator
from rest_framework.throttling import AnonRateThrottle
from mainsite.models import Product,Order
from .serializers import OrderSerializer
from utils.helpers.permissions import ApiKeyPermission
from rest_framework.exceptions import ValidationError
from .serializers import OrderSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction, DatabaseError
import json


paginator = CustomPaginator()

class ProductViewSetAPI(APIView):
    
    permission_classes = (ApiKeyPermission,)

    throttle_classes = [AnonRateThrottle,]
    
    def get(self, request):
        try:
            products = list(Product.objects.values())
            return SuccessResponse({"products": products}, status=200)
        except DatabaseError:
            return ErrorResponse({"error": "Database error occurred"}, status=500)
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            product = Product.objects.create(
                name=data["name"],
                description=data["description"],
                price=float(data["price"]),
                stock=int(data["stock"])
            )
            return SuccessResponse({"message": "Product added successfully", "product_id": product.id}, status=201)
        except (KeyError, ValueError, TypeError):
            return ErrorResponse({"error": "Invalid product data"}, status=400)
        except DatabaseError:
            return ErrorResponse({"error": "Database error occurred"}, status=500)

    
class OrderViewSetAPI(APIView):

    permission_classes = (ApiKeyPermission,)
    throttle_classes = [AnonRateThrottle]

    def create(self, request):
        try:
            products_data = request.data.get("products", [])
            total_price = 0
            product_instances = []

            for item in products_data:
                product = Product.objects.get(id=item['id'])
                if product.stock < item['quantity']:
                    raise ValidationError({"error": f"Insufficient stock for {product.name}"})
                product.stock -= item['quantity']
                product_instances.append(product)
                total_price += product.price * item['quantity']
            
            for product in product_instances:
                product.save()
            
            order = Order.objects.create(products=products_data, total_price=total_price, status='pending')
            return SuccessResponse(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return ErrorResponse({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return ErrorResponse(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ErrorResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
