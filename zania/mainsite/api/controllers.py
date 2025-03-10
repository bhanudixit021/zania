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
from django.core.exceptions import ObjectDoesNotExist
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

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            products_data = data.get("products", [])
            if not products_data:
                return ErrorResponse({"error": "No products provided"}, status=400)
            
            total_price = 0
            product_instances = []
            
            with transaction.atomic():
                for item in products_data:
                    product = Product.objects.get(id=item['id'])
                    if product.stock < item['quantity']:
                        return ErrorResponse({"error": f"Insufficient stock for {product.name}"}, status=400)
                    product.stock -= item['quantity']
                    product_instances.append(product)
                    total_price += product.price * item['quantity']
                
                for product in product_instances:
                    product.save()
                
                order = Order.objects.create(products=products_data, total_price=total_price, status='pending')
                return SuccessResponse({"message": "Order placed successfully", "order_id": order.id}, status=201)
        except ObjectDoesNotExist:
            return ErrorResponse({"error": "Product not found"}, status=404)
        except (KeyError, ValueError, TypeError):
            return ErrorResponse({"error": "Invalid order data"}, status=400)
        except DatabaseError:
            return ErrorResponse({"error": "Database error occurred"}, status=500)
        except Exception as e:
            return ErrorResponse({"error": str(e)}, status=500)