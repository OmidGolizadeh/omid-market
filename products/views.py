from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from .models import Product, Category, Category_brand
from django.db.models import F


class ProductView(TemplateView):
    template_name = 'products/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Product.objects.all()
        context['category'] = Category.objects.all()
        context['brand'] = Category_brand.objects.all()
        context['latest_products'] = Product.objects.order_by('-created_at')[:3]
        return context


class ProductList(TemplateView):
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Product.objects.all()
        context['category'] = Category.objects.all()
        context['brand'] = Category_brand.objects.all()
        context['latest_products'] = Product.objects.order_by('-created_at')[:3]
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Product.objects.filter(pk=obj.pk).update(view=F('view') + 1)
        obj.refresh_from_db()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['product'] = Product.objects.all()
        context['product_offer'] = Product.objects.exclude(pk=self.object.pk)[:5]
        return context
