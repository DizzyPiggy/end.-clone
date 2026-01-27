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

    def create_invoice(self, order_id, amount, currency='usd', description='', success_url=None, cancel_url=None):
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Payload construction
        payload = {
            "price_amount": float(amount),
            "price_currency": currency,
            "order_id": str(order_id),
            "order_description": description,
            # "ipn_callback_url": "...", # Optional, set in dashboard or settings
        }
        
        if success_url:
            payload['success_url'] = success_url
        if cancel_url:
            payload['cancel_url'] = cancel_url
        
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
