import json
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from apps.orders.models import Order
from .services import NowPaymentsService

from django.urls import reverse

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # You might have a form here to choose crypto currency if desired,
        # but for now we'll just initiate the invoice which lets user choose on NOWPayments page 
        # or we pass a default if needed.
        pass
    
    # Initiative payment
    service = NowPaymentsService()
    # Using 'usd' as base currency, assuming product prices are in USD
    # You can change this based on project requirements
    
    success_url = request.build_absolute_uri(reverse('orders:payment_success'))
    failed_url = request.build_absolute_uri(reverse('orders:payment_failed'))
    
    response = service.create_invoice(
        order_id=order.id,
        amount=order.get_total_cost(),
        currency='usd',
        description=f'Order {order.id}',
        success_url=success_url,
        cancel_url=failed_url
    )
    
    if response and 'invoice_url' in response:
        return redirect(response['invoice_url'])
    else:
        # Handle error
        return render(request, 'payments/error.html', {'error': 'Could not initiate payment.'})

@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        service = NowPaymentsService()
        signature = request.headers.get('x-nowpayments-sig')
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON')
            
        if service.check_signature(data, signature):
            # Signature is valid
            order_id = data.get('order_id')
            payment_status = data.get('payment_status')
            payment_id = data.get('payment_id') # or id from invoice
            
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return HttpResponseBadRequest('Order not found')
            
            # Update order based on status
            # statuses: waiting, confirming, confirmed, sending, partially_paid, finished, failed, refunded, expired
            if payment_status == 'finished' or payment_status == 'confirmed':
                order.paid = True
                order.status = 'paid'
                order.nowpayments_id = str(data.get('payment_id'))
                order.save()
            elif payment_status == 'failed' or payment_status == 'expired':
                order.status = 'cancelled' # or failed
                order.save()
                
            return HttpResponse('OK')
        else:
            return HttpResponseBadRequest('Invalid Signature')
            
    return HttpResponseBadRequest('Invalid Method')
