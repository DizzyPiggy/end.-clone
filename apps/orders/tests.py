from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from apps.catalog.models import Product
from .models import Order, OrderItem
from apps.cart.service import Cart
from decimal import Decimal

class OrderCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('100.00'),
            description='Test Description'
        )
        self.url = reverse('orders:order_create')

    def test_order_create_view_get_empty_cart(self):
        response = self.client.get(self.url)
        # Should redirect to catalog because cart is empty
        self.assertRedirects(response, reverse('catalog:product_list'))

    def test_order_create_view_post_success(self):
        # Add item to cart
        session = self.client.session
        cart = {
            f'{self.product.id}-M': {
                'product_id': str(self.product.id),
                'quantity': 1,
                'price': str(self.product.price),
                'size': 'M'
            }
        }
        session[settings.CART_SESSION_ID] = cart
        session.save()

        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'New York'
        }
        
        response = self.client.post(self.url, data)
        
        # Check if order created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)
        
        # Check redirection to payment process
        self.assertRedirects(response, reverse('payments:process'))
        
        # Check if cart is cleared
        session = self.client.session
        # Check if cart is cleared (it might be re-created as empty by context processors on the redirected page)
        cart = session.get(settings.CART_SESSION_ID)
        self.assertEqual(cart, {})
