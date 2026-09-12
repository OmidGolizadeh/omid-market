from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from products.models import Product
from .cart_module import Cart


# Create your views here.


class CartView(TemplateView):
    template_name = 'cart/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.all()
        cart = Cart(self.request)
        context['product'] = product
        context['recommended_products'] = product.order_by('-view')[:5]
        context['cart'] = cart
        context['total_price_all'] = cart.get_total_price_all()
        context['total_price'] = cart.get_total_price()
        context['total_discount'] = cart.get_total_discount()
        return context


class CartAddView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        color, warranty, number = request.POST.get('color'), request.POST.get('warranty'), request.POST.get('number')
        cart = Cart(request)
        cart.add(product, number, color, warranty)
        return redirect('cart:cart_detail')


class CartDelete(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.delete(id)
        return redirect('cart:cart_detail')


class CartDeleteAll(View):
    def get(self, request):
        cart = Cart(request)
        cart.delete_all()
        return redirect('cart:cart_detail')
