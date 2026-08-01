from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('products', views.Product_view.as_view(), name='product'),
    path('productlist', views.Product_list.as_view(), name='product_list'),
]
