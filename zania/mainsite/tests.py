from django.test import TestCase, Client
from .models import Product
from django.urls import reverse
import json

class EcommerceAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_key = {"APIKEY": "default-api-key"}
        self.product = Product.objects.create(name="Test Product", description="Test Desc", price=10.0, stock=5)

    def test_get_products(self):
        response = self.client.get(reverse('product-list'), headers=self.api_key)
        self.assertEqual(response.status_code, 200)
        self.assertIn("products", response.json())

    def test_add_product(self):
        data = {"name": "New Product", "description": "Desc", "price": 20.0, "stock": 10}
        response = self.client.post(reverse('product-list'), data=json.dumps(data), content_type='application/json', headers=self.api_key)
        self.assertEqual(response.status_code, 201)

    def test_place_order_success(self):
        order_data = {"products": [{"id": self.product.id, "quantity": 2}]}
        response = self.client.post(reverse('order-create'), data=json.dumps(order_data), content_type='application/json', headers=self.api_key)
        self.assertEqual(response.status_code, 201)

    def test_place_order_insufficient_stock(self):
        order_data = {"products": [{"id": self.product.id, "quantity": 10}]}
        response = self.client.post(reverse('order-create'), data=json.dumps(order_data), content_type='application/json', headers=self.api_key)
        self.assertEqual(response.status_code, 400)