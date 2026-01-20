from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Order, OrderItem
from .forms import OrderCreateForm
from apps.cart.service import Cart

def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('catalog:product_list') # Redirect to catalog if cart is empty

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
            # Clear the cart
            cart.clear()
            
            # Set the order in session to associate with payment later if needed, 
            # or just pass ID to payment view.
            request.session['order_id'] = order.id
            
            return redirect(reverse('payments:process'))
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order/confirmed.html', {'order': order})
