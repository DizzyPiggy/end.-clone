from django.contrib import admin
from .models import Category, Product, Clothing, Footwear, Accessory, ProductImage, ProductSize, Brand, ProductBrand

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductBrandInline(admin.TabularInline):
    model = ProductBrand
    extra = 1

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__name',)

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size')
    list_filter = ('size',)
    search_fields = ('product__name', 'size')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('product', 'brand')
    search_fields = ('product__name', 'brand__name')

class BaseProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'brand_display', 'base_color', 'color', 'category', 'in_stock')
    list_filter = ('category', 'base_color', 'product_brands__brand')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSizeInline, ProductImageInline, ProductBrandInline]

@admin.register(Product)
class ProductAdmin(BaseProductAdmin):
    pass

@admin.register(Clothing)
class ClothingAdmin(BaseProductAdmin):
    list_display = BaseProductAdmin.list_display + ('fit',)
    list_filter = BaseProductAdmin.list_filter + ('fit',)

@admin.register(Footwear)
class FootwearAdmin(BaseProductAdmin):
    list_display = BaseProductAdmin.list_display + ('height',)
    list_filter = BaseProductAdmin.list_filter + ('height',)

@admin.register(Accessory)
class AccessoryAdmin(BaseProductAdmin):
    list_display = BaseProductAdmin.list_display + ('type',)
    list_filter = BaseProductAdmin.list_filter + ('type',)
