from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('products', views.ProductView.as_view(), name='product'),
    path('productlist', views.ProductList.as_view(), name='product_list'),
    path('productdetaill/<slug:slug>', views.ProductDetail.as_view(), name='product_detail'),
    path('like/<slug:slug>/<int:pk>', views.like_view, name='like'),
    path('search', views.Search_view.as_view(), name='search'),
    path('compare', views.CompareView.as_view(), name='compare'),
    path('compare/add/<int:pk>', views.CompareAdd.as_view(), name='compare_add'),
    path('compare/remove/<int:pk>', views.CompareDelete.as_view(), name='compare_remove'),
]
