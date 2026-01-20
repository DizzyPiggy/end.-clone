import json
import hmac
import hashlib
import requests
from django.conf import settings

class NowPaymentsService:
    API_URL = 'https://api.nowpayments.io/v1/invoice'
    
    def __init__(self):
        self.api_key = settings.NOWPAYMENTS_API_KEY
        self.ipn_secret = settings.NOWPAYMENTS_IPN_SECRET

    def create_invoice(self, order_id, amount, currency='usd', description=''):
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Webhook URL construction
        # Note: For localhost, this won't be reachable by NOWPayments without a tunnel.
        # This assumes the domain is configured in settings or via request if passed.
        # But here we just assume a standard path relative to site domain if we had one.
        # Ideally, we should use `reverse` with a full domain, but we'll leave ipn_callback_url empty
        # or require it to be set in settings if needed. 
        # The docs say ipn_callback_url is optional in request if set in dashboard.
        # Let's try to send it if we can, but simpler to omit if not strictly required for this stage.
        # Actually, let's include a placeholder or configurable URL.
        
        payload = {
            "price_amount": float(amount),
            "price_currency": currency,
            "order_id": str(order_id),
            "order_description": description,
            "ipn_callback_url": "https://your-domain.com/payments/webhook/", # Placeholder
            "success_url": "https://your-domain.com/orders/confirmation/{}/".format(order_id), # Placeholder
            "cancel_url": "https://your-domain.com/cart/" # Placeholder
        }
        
        try:
            response = requests.post(self.API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Log error
            print(f"NOWPayments API Error: {e}")
            if response:
                print(f"Response: {response.text}")
            return None

    def check_signature(self, request_data, signature):
        """
        Verify the IPN signature from NOWPayments.
        """
        if not signature:
            return False
            
        # Sort the dictionary by keys
        sorted_data = dict(sorted(request_data.items()))
        
        # Convert to JSON string with separators and no spaces, sorted keys
        # Python's json.dumps with sort_keys=True matches the requirement fairly well,
        # but exact format matters. Docs say:
        # JSON.stringify (params, Object.keys(params).sort())
        # Python example in docs:
        # sorted_msg = json.dumps(message, separators=(',', ':'), sort_keys=True)
        
        # We need to filter out 'x-nowpayments-sig' if it's in the data (usually it's in header)
        
        sorted_msg = json.dumps(sorted_data, separators=(',', ':'), sort_keys=True)
        
        digest = hmac.new(
            str(self.ipn_secret).encode(),
            sorted_msg.encode(),
            hashlib.sha512
        )
        calculated_signature = digest.hexdigest()
        
        return calculated_signature == signature
