from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .service import Cart
from apps.catalog.models import Product

def cart_detail_view(request):
    cart = Cart(request)
    context = {
        'cart': cart,
        'total_price': cart.get_total_price()
    }
    if request.headers.get('HX-Request'):
         return render(request, 'partials/cart_drawer.html', context)
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def add_to_cart_view(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, size=size, quantity=quantity)
    
    context = {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'cart_total_items': len(cart),
        'open_drawer': True,
        'update_badge': True
    }
    return render(request, 'cart/partials/cart_drawer_content.html', context)

@require_POST
def update_cart_item_view(request, item_id):
    """
    item_id is the composite key "product_id-size"
    """
    cart = Cart(request)
    quantity = int(request.POST.get('quantity'))
    
    # We need to split the key to get product_id and size
    try:
        product_id, size = item_id.split('-')
        product = get_object_or_404(Product, id=product_id)
        
        if quantity > 0:
            cart.add(product=product, size=size, quantity=quantity, override_quantity=True)
        else:
            cart.remove(product_id, size)
            
    except ValueError:
        pass # Handle invalid key format if needed

    context = {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'cart_total_items': len(cart),
        'update_badge': True
    }
    return render(request, 'cart/partials/cart_drawer_content.html', context)

@require_POST
def remove_from_cart_view(request, item_id):
    """
    item_id is the composite key "product_id-size"
    """
    cart = Cart(request)
    try:
        product_id, size = item_id.split('-')
        cart.remove(product_id, size)
    except ValueError:
        pass

    context = {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'cart_total_items': len(cart),
        'update_badge': True
    }
    return render(request, 'cart/partials/cart_drawer_content.html', context)
