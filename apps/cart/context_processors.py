from .service import Cart

def cart_context(request):
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_total_items': len(cart),
        'total_price': cart.get_total_price()
    }
