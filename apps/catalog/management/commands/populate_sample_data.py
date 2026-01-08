from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Clothing, Footwear, Accessory, ProductSize, Product, ProductImage
from django.utils.text import slugify
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate database with sample data from screenshots'

    def handle(self, *args, **options):
        self.stdout.write('Populating database...')

        # Categories
        clothing_cat, _ = Category.objects.get_or_create(name='Clothing', description='Apparel and wear')
        footwear_cat, _ = Category.objects.get_or_create(name='Footwear', description='Shoes and sneakers')
        accessories_cat, _ = Category.objects.get_or_create(name='Accessories', description='Watches, bags, and more')

        # Footwear Data
        footwear_items = [
            {'name': 'Adidas x SPZL Samoa II Sneaker', 'brand': 'Adidas', 'price': 145.00, 'height': 'low'},
            {'name': 'adidas Adistar XLG 2.0 Sneaker', 'brand': 'Adidas', 'price': 159.00, 'height': 'low'},
            {'name': 'adidas Handball Spezial W', 'brand': 'Adidas', 'price': 119.00, 'height': 'low'},
            {'name': 'Birkenstock Boston', 'brand': 'Birkenstock', 'price': 185.00, 'height': 'low'},
            {'name': 'New Balance 2002DX Sneaker', 'brand': 'New Balance', 'price': 199.00, 'height': 'low'},
            {'name': "Air Jordan 1 Retro Low OG 'Chicago' Sneaker", 'brand': 'Air Jordan', 'price': 190.00, 'height': 'low'},
            {'name': 'Air Jordan x A Ma Maniere Air Jordan 6 Retro', 'brand': 'Air Jordan', 'price': 275.00, 'height': 'mid'},
            {'name': 'adidas Bw Army Sneaker', 'brand': 'Adidas', 'price': 170.00, 'height': 'low'},
        ]


        for item in footwear_items:
             obj, created = Footwear.objects.get_or_create(
                name=item['name'],
                defaults={
                    'category': footwear_cat,
                    'price': item['price'],
                    # 'brand': item['brand'],
                    'description': f"Authentic {item['name']} in premium materials.",
                    # 'size' removed from here
                    'height': item['height']
                }
            )
             # Create default size
             ProductSize.objects.get_or_create(product=obj, size='US 9')
             
             if created:
                 self.stdout.write(self.style.SUCCESS(f"Created Footwear: {item['name']}"))
             else:
                 self.stdout.write(f"Footwear already exists: {item['name']}")


        # Clothing Data
        clothing_items = [
            {'name': 'Moncler Maya Down Jacket', 'brand': 'Moncler', 'price': 1699.00},
            {'name': 'Carhartt WIP Duck Duck T-Shirt', 'brand': 'Carhartt WIP', 'price': 55.00},
            {'name': 'Patagonia Better Sweater Vest', 'brand': 'Patagonia', 'price': 149.00},
            {'name': 'END. x Universal Works Snug Bomber', 'brand': 'Universal Works', 'price': 225.00},
            {'name': 'END. Beer Mat T-Shirt', 'brand': 'END. Label', 'price': 79.00},
            {'name': 'MKI Chunky Rib Knit Hoodie', 'brand': 'MKI', 'price': 115.00},
            {'name': 'Canada Goose Crofton Jacket', 'brand': 'Canada Goose', 'price': 1009.00},
            {'name': "Arc'teryx Beta SL Jacket", 'brand': "Arc'teryxe", 'price': 595.00},
        ]

        for item in clothing_items:
            obj, created = Clothing.objects.get_or_create(
                name=item['name'],
                defaults={
                    'category': clothing_cat,
                    'price': item['price'],
                    # 'brand': item['brand'],
                    'description': f"Premium {item['name']} for your wardrobe.",
                    # 'size' removed
                    'material': 'Cotton/Polyester Blend',
                    'fit': 'regular'
                }
            )
            # Create default size
            ProductSize.objects.get_or_create(product=obj, size='M')
            
            if created:
                 self.stdout.write(self.style.SUCCESS(f"Created Clothing: {item['name']}"))
            else:
                 self.stdout.write(f"Clothing already exists: {item['name']}")

        # Accessories Data
        accessory_items = [
            {'name': 'Casio Vintage Digital Watch', 'brand': 'Casio', 'price': 79.00, 'type': 'other'},
            {'name': 'Carhartt WIP Chrome Clip Belt', 'brand': 'Carhartt WIP', 'price': 39.00, 'type': 'belt'},
            {'name': '47 NY Yankees Clean Up Cap', 'brand': '47 Brand', 'price': 35.00, 'type': 'hat'},
            {'name': 'Gottlob Edition 1 Bracelet', 'brand': 'Gottlob', 'price': 105.00, 'type': 'jewelry'},
            {'name': 'G-Shock x Central Cee DW-6900CC25-4ER Watch', 'brand': 'G-Shock', 'price': 169.00, 'type': 'other'},
            {'name': 'BEAMS JAPAN x Hightide Card Case', 'brand': 'BEAMS JAPAN', 'price': 25.00, 'type': 'other'},
            {'name': 'END. x The Great Frog x 47 Brand Hitch Cap', 'brand': '47 Brand', 'price': 59.00, 'type': 'hat'},
            {'name': 'BEAMS JAPAN Mt. Fuji Key Chain', 'brand': 'BEAMS JAPAN', 'price': 25.00, 'type': 'other'},
        ]

        for item in accessory_items:
            obj, created = Accessory.objects.get_or_create(
                name=item['name'],
                defaults={
                    'category': accessories_cat,
                    'price': item['price'],
                    # 'brand': item['brand'],
                    'description': f"Stylish {item['name']} accessory.",
                    'type': item['type'],
                    # 'size' removed
                    'material': 'Mixed Materials'
                }
            )
            # Create default size
            ProductSize.objects.get_or_create(product=obj, size='One Size')

            if created:
                 self.stdout.write(self.style.SUCCESS(f"Created Accessory: {item['name']}"))
            else:
                 self.stdout.write(f"Accessory already exists: {item['name']}")

        # --- Populate Product Images from media/productimages ---
        self.stdout.write('Scanning media/productimages for galleries...')
        product_images_root = os.path.join(settings.MEDIA_ROOT, 'productimages')
        
        if os.path.exists(product_images_root):
            for product_name_folder in os.listdir(product_images_root):
                folder_path = os.path.join(product_images_root, product_name_folder)
                
                if os.path.isdir(folder_path):
                    # Try to find the product matching the folder name
                    product = None
                    try:
                        product = Product.objects.get(name=product_name_folder)
                    except Product.DoesNotExist:
                        # Try case-insensitive match
                        products = Product.objects.filter(name__iexact=product_name_folder)
                        if products.exists():
                             product = products.first()
                             self.stdout.write(self.style.WARNING(f"Matched '{product_name_folder}' to '{product.name}' (case-insensitive)"))
                        else:
                             # Try matching with replaced typos (e.g. ll vs II)
                             # Common issue: matches 'Samoa ll' (els) to 'Samoa II' (eyes)
                             if 'll' in product_name_folder:
                                 repl = product_name_folder.replace('ll', 'II')
                                 try:
                                     product = Product.objects.get(name=repl)
                                     self.stdout.write(self.style.WARNING(f"Matched '{product_name_folder}' to '{product.name}' (typo fix ll->II)"))
                                 except Product.DoesNotExist:
                                     pass

                    if not product:
                        self.stdout.write(self.style.ERROR(f"Product not found for folder: '{product_name_folder}'"))
                        continue

                    # Scan images inside the folder
                    for image_file in os.listdir(folder_path):
                        if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                            # Construct relative path for ImageField
                            # The path should be relative to MEDIA_ROOT
                            relative_path = os.path.join('productimages', product_name_folder, image_file).replace('\\', '/')
                            
                            img_obj, created = ProductImage.objects.get_or_create(
                                product=product,
                                image=relative_path
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"Added image {image_file} to {product.name}"))
                            else:
                                self.stdout.write(f"Image {image_file} already exists for {product.name}")
        else:
             self.stdout.write(self.style.WARNING(f"Directory {product_images_root} does not exist."))


        self.stdout.write(self.style.SUCCESS('Database population completed successfully.'))
