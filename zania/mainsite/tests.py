from django.test import TestCase

# Create your tests here.

from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product

class EcommerceAPITest(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Laptop", description="A powerful laptop", price=1000, stock=10)
    
    def test_get_products(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_product(self):
        data = {"name": "Phone", "description": "A smartphone", "price": 500, "stock": 5}
        response = self.client.post("/products/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_order_insufficient_stock(self):
        data = {"products": [{"id": self.product.id, "quantity": 20}]}
        response = self.client.post("/orders/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
