from django.shortcuts import render, get_object_or_404
from .models import Product, Category
import random

def home(request):
    # New In: Clothing only, 10 items (2 rows)
    new_in = Product.objects.filter(category__name__iexact='clothing').order_by('-created_at')[:10]
    
    # Sneakers: Footwear only, 10 items (2 rows)
    sneakers = Product.objects.filter(category__name__iexact='footwear').order_by('-created_at')[:10]
    
    context = {
        'new_in': new_in,
        'sneakers': sneakers
    }
    return render(request, 'pages/home.html', context)

def women(request):
    return render(request, 'pages/women.html')

from django.db.models import Max, Q

def product_list(request):
    products = Product.objects.all().select_related('category').prefetch_related('product_brands__brand')
    category_name = request.GET.get('category')
    search_query = request.GET.get('q')
    
    # 0. Search Filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # 1. Base Filter (Category)
    if category_name:
        products = products.filter(category__name__iexact=category_name)
    
    # 2. Dynamic Max Price (based on current scope)
    max_price_val = products.aggregate(Max('price'))['price__max']
    max_price_limit = int(max_price_val) if max_price_val else 1000

    # --- Capture Available Facets (Optimization) ---
    # Determine which brands/colors exist in the current category scope *before* other filters apply
    # This prevents showing "Adidas" in "Clothing" if Adidas only makes Footwear.
    available_brand_ids = products.values_list('product_brands__brand', flat=True).distinct()
    available_colors = set(products.values_list('base_color', flat=True).distinct())

    # 3. Apply Filters
    selected_brands = request.GET.getlist('brand')
    selected_colors = request.GET.getlist('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if selected_brands:
        products = products.filter(product_brands__brand__id__in=selected_brands).distinct()
    
    if selected_colors:
        products = products.filter(base_color__in=selected_colors)

    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)

    # Default ordering if not filtered by relevance or other
    # Optimization: Avoid order_by('?') for DoS protection
    # For large datasets, we should implement a better strategy (e.g. shuffling a list of IDs)
    # For now, we'll order by created_at. If random is needed, we should select IDs first.
    products = products.order_by('-created_at')

    # 4. Context Data
    from .models import Brand
    # Only available brands
    all_brands = Brand.objects.filter(id__in=available_brand_ids).order_by('name')
    
    # Filter BaseColor choices to only valid ones
    all_colors = [c for c in Product.BaseColor.choices if c[0] in available_colors]

    context = {
        'products': products,
        'current_category': category_name,
        'all_brands': all_brands,
        'all_colors': all_colors,
        'max_price_limit': max_price_limit,
    }
    
    # Only return partial if specifically requesting the product grid (e.g. from filters)
    if request.headers.get('HX-Request') and request.headers.get('HX-Target') == 'product-grid':
        return render(request, 'catalog/partials/filtered_results.html', context)
        
    return render(request, 'catalog/product_list.html', context)

def product_detail(request, pk):
    # Optimize main product query
    queryset = Product.objects.select_related(
        'category', 
        'clothing', 
        'footwear', 
        'accessory'
    ).prefetch_related(
        'gallery_images', 
        'sizes'
    )
    product = get_object_or_404(queryset, pk=pk)
    
    # Get 4 random products from the same category, excluding current product
    # Optimization: Avoid order_by('?') for DoS protection
    related_qs = Product.objects.filter(category=product.category).exclude(pk=pk)
    all_related_ids = list(related_qs.values_list('id', flat=True))
    
    if len(all_related_ids) > 4:
        random_ids = random.sample(all_related_ids, 4)
        # Prefetch images for related products to avoid N+1 in template loop
        related_products = Product.objects.filter(id__in=random_ids).prefetch_related('gallery_images')
    else:
        related_products = related_qs.prefetch_related('gallery_images')
    
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'catalog/product_detail.html', context)
