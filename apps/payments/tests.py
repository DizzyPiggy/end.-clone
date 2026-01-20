import json
import hashlib
import hmac
from unittest.mock import patch
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.conf import settings
from apps.orders.models import Order
from .services import NowPaymentsService

class PaymentServiceTest(TestCase):
    def setUp(self):
        self.service = NowPaymentsService()
        self.order = Order.objects.create(
            first_name='Test', last_name='User', email='test@test.com',
            address='Street', postal_code='123', city='City'
        )

    @patch('requests.post')
    def test_create_invoice(self, mock_post):
        mock_response = {'invoice_url': 'https://nowpayments.io/payment/?iid=123'}
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        result = self.service.create_invoice(self.order.id, 100)
        self.assertEqual(result, mock_response)
        
    def test_check_signature(self):
        secret = settings.NOWPAYMENTS_IPN_SECRET
        data = {'key': 'value', 'order_id': '1'}
        
        # Calculate expected signature
        sorted_data = json.dumps(data, separators=(',', ':'), sort_keys=True)
        digest = hmac.new(str(secret).encode(), sorted_data.encode(), hashlib.sha512)
        signature = digest.hexdigest()
        
        self.assertTrue(self.service.check_signature(data, signature))
        self.assertFalse(self.service.check_signature(data, 'wrong_signature'))

class PaymentWebhookTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('payments:webhook')
        self.order = Order.objects.create(
            first_name='Test', last_name='User', email='test@test.com',
            address='Street', postal_code='123', city='City'
        )
        self.secret = settings.NOWPAYMENTS_IPN_SECRET

    def test_webhook_success(self):
        payload = {
            'payment_status': 'finished',
            'payment_id': '12345',
            'price_amount': 100,
            'price_currency': 'usd',
            'pay_amount': 100,
            'pay_currency': 'btc',
            'order_id': str(self.order.id),
            'order_description': 'Test',
            'ipn_id': 'unique_id',
            'created_at': '2021-01-01T00:00:00.000Z',
            'updated_at': '2021-01-01T00:00:00.000Z',
            'purchase_id': 'pid',
            'outcome_amount': 100,
            'outcome_currency': 'usd'
        }
        
        # Calculate signature
        # Important: payload in webhook is usually flattened or simple dict.
        # check_signature sorts keys.
        sorted_data = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        digest = hmac.new(str(self.secret).encode(), sorted_data.encode(), hashlib.sha512)
        signature = digest.hexdigest()
        
        response = self.client.post(
            self.url,
            data=payload,
            content_type='application/json',
            HTTP_X_NOWPAYMENTS_SIG=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh order
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertEqual(self.order.status, 'paid')
        self.assertEqual(self.order.nowpayments_id, '12345')
