from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Product, Category, Category_brand


class Product_view(TemplateView):
    template_name = 'products/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Product.objects.all()
        context['category'] = Category.objects.all()
        context['brand'] = Category_brand.objects.all()
        return context


class Product_list(TemplateView):
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Product.objects.all()
        context['category'] = Category.objects.all()
        context['brand'] = Category_brand.objects.all()
        return context
