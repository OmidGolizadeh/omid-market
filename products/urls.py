from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('products', views.ProductView.as_view(), name='product'),
    path('productlist', views.ProductList.as_view(), name='product_list'),
    path('productdetaill/<slug:slug>', views.ProductDetail.as_view(), name='product_detail'),
]
