from .service import Cart

def cart_context(request):
    return {
        'cart_total_items': len(Cart(request))
    }
