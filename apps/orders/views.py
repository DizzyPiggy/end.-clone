from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from .models import Order, OrderItem
from .forms import OrderCreateForm
from apps.cart.service import Cart

def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('catalog:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                    size=item['size']
                )
            cart.clear()
            request.session['order_id'] = order.id
            
            # For HTMX, we need to stop the browser from following the redirect chain via XHR.
            # We return a 200 OK with HX-Redirect, which HTMX interprets as a command 
            # to change window.location.
            if request.headers.get('HX-Request'):
                response = HttpResponse("Redirecting...")
                response['HX-Redirect'] = reverse('payments:process')
                return response
                
            return redirect('payments:process')
    else:
        form = OrderCreateForm()
    
    context = {'cart': cart, 'form': form}
    
    return render(request, 'orders/order/create.html', context)

def order_confirmation(request, order_id):
    # Verify the order belongs to the current session (basic IDOR protection)
    # Ideally, for logged-in users, we check request.user. For guests, we rely on session.
    session_order_id = request.session.get('order_id')
    if not session_order_id or str(session_order_id) != str(order_id):
        # Fallback or redirect if they try to access someone else's order
        return redirect('catalog:product_list')
        
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order/confirmed.html', {'order': order})

def payment_success(request):
    return render(request, 'orders/payment/success.html')

def payment_failed(request):
    return render(request, 'orders/payment/failed.html')

def payment_waiting(request):
    return render(request, 'orders/payment/waiting.html')
