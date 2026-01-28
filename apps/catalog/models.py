from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # brand field removed
    
    @property
    def brand_display(self):
        # Use .all() to leverage prefetch_related cache if available
        # This avoids hitting the DB for every product if prefetched
        brands = self.product_brands.all()
        return brands[0].brand.name if brands else ""

    # KEEP image field for the main thumbnail
    image = models.ImageField(upload_to='products/', blank=True, null=True, max_length=500)
    
    # Add color field
    color = models.CharField(max_length=100, blank=True, null=True) 
    
    class BaseColor(models.TextChoices):
        BLACK = 'Black', 'Black'
        WHITE = 'White', 'White'
        GREY = 'Grey', 'Grey'
        BLUE = 'Blue', 'Blue'
        RED = 'Red', 'Red'
        GREEN = 'Green', 'Green'
        YELLOW = 'Yellow', 'Yellow'
        ORANGE = 'Orange', 'Orange'
        BURGUNDY = 'Burgundy', 'Burgundy'
        PURPLE = 'Purple', 'Purple'
        BROWN = 'Brown', 'Brown'
        BEIGE = 'Beige', 'Beige'
        PINK = 'Pink', 'Pink'
        MULTI = 'Multi', 'Multi'

    base_color = models.CharField(
        max_length=20, 
        choices=BaseColor.choices, 
        blank=True, 
        null=True, 
        db_index=True
    ) 
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductBrand(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_brands')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='brand_products')

    class Meta:
        verbose_name = "Product Brand"
        verbose_name_plural = "Product Brands"

    def __str__(self):
        return f"{self.brand.name} for {self.product.name}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='product_gallery/', max_length=500)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images (Gallery)"

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Product Size"
        verbose_name_plural = "Product Sizes"

    def __str__(self):
        return f"{self.product.name} - {self.size}"

class Clothing(Product):
    FIT_CHOICES = [
        ('slim', 'Slim Fit'),
        ('regular', 'Regular Fit'),
        ('oversized', 'Oversized'),
    ]
    # Removed size field
    material = models.CharField(max_length=100)
    fit = models.CharField(max_length=20, choices=FIT_CHOICES)

class Footwear(Product):
    HEIGHT_CHOICES = [
        ('low', 'Low Top'),
        ('mid', 'Mid Top'),
        ('high', 'High Top'),
    ]
    # Removed size field
    height = models.CharField(max_length=10, choices=HEIGHT_CHOICES)

class Accessory(Product):
    TYPE_CHOICES = [
        ('bag', 'Bag'),
        ('hat', 'Hat'),
        ('belt', 'Belt'),
        ('jewelry', 'Jewelry'),
        ('other', 'Other'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    # Removed size field
    material = models.CharField(max_length=100)
