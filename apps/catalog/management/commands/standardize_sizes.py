from django.core.management.base import BaseCommand
from apps.catalog.models import Footwear, Accessory, ProductSize

class Command(BaseCommand):
    help = 'Standardize sizes for Footwear and Accessories'

    def handle(self, *args, **kwargs):
        footwear_sizes = ['US 6.5', 'US 7', 'US 7.5', 'US 8', 'US 8.5', 'US 9', 'US 9.5', 'US 10', 'US 10.5', 'US 11']
        accessory_sizes = ['One Size']

        # Update Footwear
        footwear_products = Footwear.objects.all()
        self.stdout.write(f'Found {footwear_products.count()} footwear products.')

        for product in footwear_products:
            # Clear existing sizes
            # Since Footwear inherits from Product, 'product' here refers to the Footwear instance,
            # but because of Multi-Table Inheritance, it acts as a Product instance too.
            # We access the related ProductSize objects via the 'sizes' related manager defined in ProductSize.
            product.sizes.all().delete()
            
            # Create new sizes
            for size in footwear_sizes:
                ProductSize.objects.create(product=product, size=size)
        
        self.stdout.write(self.style.SUCCESS(f'Updated sizes for {footwear_products.count()} footwear products.'))

        # Update Accessories
        accessory_products = Accessory.objects.all()
        self.stdout.write(f'Found {accessory_products.count()} accessory products.')

        for product in accessory_products:
            product.sizes.all().delete()
            for size in accessory_sizes:
                ProductSize.objects.create(product=product, size=size)

        self.stdout.write(self.style.SUCCESS(f'Updated sizes for {accessory_products.count()} accessory products.'))
