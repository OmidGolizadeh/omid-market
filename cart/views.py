from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, DetailView, CreateView
from products.models import Product
from accounts.models import Address
from .models import Order, OrderItem
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
        color, warranty, number, size = request.POST.get('color'), request.POST.get('warranty'), request.POST.get(
            'number'), request.POST.get('size')
        cart = Cart(request)
        cart.add(product, number, color, warranty, size)
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


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'cart/checkout.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address_id = self.request.session.get('select_address_user')
        if address_id:
            context['address_user'] = Address.objects.filter(id=address_id, user=self.request.user)
        else:
            context['address_user'] = None
        return context


class SelectAddress(LoginRequiredMixin, View):

    def post(self, request, pk):
        address_id = request.POST.get('select_address')
        if address_id:
            address = Address.objects.filter(id=address_id, user=request.user).select_related(
                'province',
                'city').first()
            self.request.session['select_address_user'] = address.id
        return redirect('cart:order_detail', pk=pk)


class OrderCreate(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user, total_price=cart.get_total_price_all())
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], size=item['size'], color=item['color'],
                                     warranty=item['warranty'], number=item['number'], price=item['price'])
            cart.delete_all()
        return redirect('cart:order_detail', order.id)
