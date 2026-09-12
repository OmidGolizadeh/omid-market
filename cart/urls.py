from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('cart_detail', views.CartView.as_view(), name='cart_detail'),
    path('cart_add/<int:pk>', views.CartAddView.as_view(), name='cart_add'),
    path('cart_delete/<str:id>', views.CartDelete.as_view(), name='cart_delete'),
    path('cart_delete_all', views.CartDeleteAll.as_view(), name='cart_delete_all'),
]
