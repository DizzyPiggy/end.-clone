from decimal import Decimal
from django.conf import settings
from apps.catalog.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, size, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        # Composite key for product and size
        product_id = str(product.id)
        cart_key = f"{product_id}-{size}"
        
        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'quantity': 0,
                'price': str(product.price),
                'size': size,
                'product_id': product_id
            }
        
        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product_id, size):
        """
        Remove a product from the cart.
        """
        cart_key = f"{product_id}-{size}"
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        
        # We need to map product objects to their IDs for easy lookup
        product_map = {str(p.id): p for p in products}

        for key, item in cart.items():
            item['product'] = product_map.get(item['product_id'])
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            item['item_id'] = key # Helper for templates/URLs to identify this specific line item
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()
