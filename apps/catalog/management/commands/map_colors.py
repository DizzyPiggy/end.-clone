
from django.core.management.base import BaseCommand
from apps.catalog.models import Product

class Command(BaseCommand):
    help = 'Maps complex color names to standardized BaseColor'

    def handle(self, *args, **options):
        products = Product.objects.all()
        count = 0
        
        for p in products:
            if not p.color:
                continue
                
            original = p.color.lower()
            mapped = None
            
            # Mapping Logic
            if 'black' in original or 'noir' in original:
                mapped = Product.BaseColor.BLACK
            elif 'white' in original or 'ecru' in original or 'cream' in original or 'ivory' in original or 'chalk' in original:
                mapped = Product.BaseColor.WHITE
            elif 'grey' in original or 'gray' in original or 'silver' in original or 'charcoal' in original or 'slate' in original:
                mapped = Product.BaseColor.GREY
            elif 'navy' in original or 'blue' in original or 'indigo' in original or 'denim' in original or 'azure' in original:
                mapped = Product.BaseColor.BLUE
            elif 'red' in original or 'burgundy' in original or 'maroon' in original or 'crimson' in original:
                mapped = Product.BaseColor.RED
            elif 'green' in original or 'olive' in original or 'khaki' in original or 'sage' in original or 'emerald' in original:
                mapped = Product.BaseColor.GREEN
            elif 'yellow' in original or 'gold' in original or 'mustard' in original:
                mapped = Product.BaseColor.YELLOW
            elif 'orange' in original or 'rust' in original or 'amber' in original:
                mapped = Product.BaseColor.ORANGE
            elif 'purple' in original or 'violet' in original or 'lilac' in original or 'plum' in original:
                mapped = Product.BaseColor.PURPLE
            elif 'brown' in original or 'tan' in original or 'chocolate' in original or 'coffee' in original:
                mapped = Product.BaseColor.BROWN
            elif 'beige' in original or 'sand' in original or 'camel' in original or 'stone' in original:
                mapped = Product.BaseColor.BEIGE
            elif 'pink' in original or 'rose' in original or 'coral' in original:
                mapped = Product.BaseColor.PINK
            elif 'multi' in original or 'pattern' in original:
                mapped = Product.BaseColor.MULTI
            
            if mapped:
                p.base_color = mapped
                p.save()
                self.stdout.write(self.style.SUCCESS(f'Mapped "{p.color}" -> {mapped}'))
                count += 1
            else:
                p.base_color = Product.BaseColor.MULTI # Default to Multi if unknown? Or leave null? User said "Multi or leave blank".
                # Let's try to default to Multi if it seems colorful, otherwise leave blank or let user decide?
                # User prompt: "If multiple matches or no match, default to 'Multi' or leave blank."
                # I'll default to leaving blank for now to avoid false positives, or MULTI if completely unknown.
                # Actually, safe bet is usually Multi for "undefined".
                self.stdout.write(self.style.WARNING(f'Could not map "{p.color}"'))

        self.stdout.write(self.style.SUCCESS(f'Successfully mapped {count} products.'))
