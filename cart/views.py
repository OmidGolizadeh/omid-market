from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, DetailView, CreateView
from products.models import Product
from accounts.models import Address
from .models import Order, OrderItem, DiscountCode
from .cart_module import Cart
from django.contrib import messages


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

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        # ----- چک انقضای کد تخفیف -----
        if order.discount_code and order.is_paid and order.code_discount > 0:
            if not order.discount_code.is_valid():
                # برگرداندن مبلغ
                order.total_price += order.code_discount
                order.code_discount = 0
                order.discount_code = None
                order.save()
                self.request.session.pop(f'discount_applied_{order.id}', None)
                messages.warning(self.request, 'مهلت کد تخفیف به پایان رسیده و از سفارش حذف شد.')

        address_id = self.request.session.get('select_address_user')
        context['discount_code'] = self.request.session.get(f'discount_code_{order.id}', 0)
        if address_id:
            context['address_user'] = Address.objects.filter(id=address_id, user=self.request.user).first()
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
        if not list(cart):
            messages.warning(request, 'سبد خرید شما خالی است')
            return redirect('cart:cart_detail')

        order = Order.objects.filter(user=request.user, is_paid=False).order_by('-created_at').first()
        if order:
            order.order_items.all().delete()
            order.total_price = cart.get_total_price_all()
            order.total_discount = cart.get_total_discount()
            order.code_discount = 0
            order.discount_code = None
            order.save()
            request.session.pop(f'discount_applied_{order.id}', None)
            request.session.pop(f'discount_code_{order.id}', None)
        else:
            order = Order.objects.create(user=request.user, total_price=cart.get_total_price_all(),
                                         total_discount=cart.get_total_discount())
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], size=item['size'], color=item['color'],
                                     warranty=item['warranty'], number=item['number'], price=item['price'],
                                     discount=item.get('discount', 0))

        return redirect('cart:order_detail', order.id)


class DiscountCodeView(View):
    def post(self, request, pk):
        code = request.POST.get('discount_code')
        order = get_object_or_404(Order, id=pk)
        discount_code = get_object_or_404(DiscountCode, name=code)
        if not discount_code.is_valid():
            messages.error(request, 'این کد تخفیف منقضی شده یا تعداد آن تمام شده است')
            return redirect('cart:order_detail', order.id)

        if order.code_discount > 0 or request.session.get(f'discount_applied_{order.id}'):
            messages.error(request, 'قبلاً روی این سفارش کد تخفیف اعمال شده است')
            return redirect('cart:order_detail', order.id)
        discount_amount = order.total_price * discount_code.discount / 100
        order.total_price -= discount_amount
        order.code_discount = discount_amount
        order.discount_code = discount_code
        order.save()

        request.session[f'discount_applied_{order.id}'] = True

        discount_code.number -= 1
        discount_code.save()
        messages.success(request, f'کد تخفیف {discount_code.discount}٪ اعمال شد')
        return redirect('cart:order_detail', order.id)
