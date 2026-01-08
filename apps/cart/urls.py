from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/', views.add_to_cart_view, name='add_to_cart'),
    path('remove/<str:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('update/<str:item_id>/', views.update_cart_item_view, name='update_cart_item'),
]
