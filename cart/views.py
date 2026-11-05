from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.generic import View, TemplateView, DetailView, CreateView
from products.models import Product, Warranty, ProductColor
from accounts.models import Address
from .models import Order, OrderItem, DiscountCode
from .cart_module import Cart
from django.contrib import messages
from .zarinpal import ZarinPal
from django.utils import timezone
from django.db.models import F


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
        color, warranty, size = request.POST.get('color'), request.POST.get('warranty'), request.POST.get('size')
        try:
            number = int(request.POST.get('number', 1))
        except (TypeError, ValueError):
            number = 1
        if number < 1:
            number = 1
        if color:
            product_color = ProductColor.objects.filter(product=product, color__name=color).first()
            stock = (product_color.number or 0) if product_color else 0
            if stock <= 0:
                messages.error(request, 'موجودی محصول با این رنگ انتخابی موجود نیست')
                return redirect('products:product_detail', slug=product.slug)
            if number > stock:
                messages.error(request, f'فقط {stock} عدد از این رنگ موجود است')
                return redirect('products:product_detail', slug=product.slug)
        warranty_price = 0
        if warranty:
            warranty_obj = Warranty.objects.filter(title=warranty).first()
            if warranty_obj and hasattr(warranty_obj, 'price') and warranty_obj.price:
                warranty_price = warranty_obj.price
        cart = Cart(request)
        cart.add(product, number, color, warranty, size, warranty_price)
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


class DiscountCodeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        code = (request.POST.get('discount_code') or '').strip()
        order = get_object_or_404(Order, id=pk, user=request.user)
        discount_code = DiscountCode.objects.filter(name=code).first()
        if not discount_code:
            messages.error(request, 'کد تخفیف نامعتبر است.')
            return redirect('cart:order_detail', order.id)

        if not discount_code.is_valid():
            messages.error(request, 'این کد تخفیف منقضی شده یا تعداد آن تمام شده است')
            return redirect('cart:order_detail', order.id)

        if order.code_discount > 0 or request.session.get(f'discount_applied_{order.id}'):
            messages.error(request, 'قبلاً روی این سفارش کد تخفیف اعمال شده است')
            return redirect('cart:order_detail', order.id)

        discount_amount = order.total_price * discount_code.discount // 100
        order.total_price -= discount_amount
        order.code_discount = discount_amount
        order.discount_code = discount_code
        order.save()

        DiscountCode.objects.filter(pk=discount_code.pk).update(number=F('number') - 1)
        request.session[f'discount_applied_{order.id}'] = True
        messages.success(request, f'کد تخفیف {discount_code.discount}٪ اعمال شد')
        return redirect('cart:order_detail', order.id)


pay = ZarinPal(merchant='00000000-0000-0000-0000-000000000000', call_back_url='http://127.0.0.1:8000/cart/verify')


class SendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        address_id = request.session.get('select_address_user')
        if address_id:
            order.address = Address.objects.get(id=address_id)
            order.save()
        response = pay.send_request(amount=order.total_price,
                                    description=f'سفارش #{order.id} - {order.user.full_name or order.user.phone_number}',
                                    email=request.user.email, mobile=request.user.phone_number)
        if isinstance(response, str):
            order.authority = response
            order.save()
            return redirect(pay.ZP_API_STARTPAY.format(authority=response))
        else:
            return render(request, 'cart/payment_result.html', {
                'message': f'Error code: {response.get("error_code")}, Error Message: {response.get("message")}',
                'success': False
            })


class VerifyView(LoginRequiredMixin, View):
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        if status != 'OK':
            return render(request, 'cart/payment_result.html', {
                'message': f'تراکنش ناموفق بوده است یا توسط کاربر لغو شده است',
                'success': False
            })
        try:
            order = Order.objects.get(authority=authority, user=request.user)
        except:
            return render(request, 'cart/payment_result.html', {
                'message': 'سفارش پیدا نشد.',
                'success': False
            })
        if order.is_paid:
            return render(request, 'cart/payment_result.html',
                          {'success': True, 'order': order,
                           'message': 'این سفارش قبلاً پرداخت شده است',
                           'ref_id': order.ref_id})
        response = pay.verify(request=request, amount=order.total_price)

        if response.get('transaction'):
            if response.get('pay'):
                order.is_paid = True
                order.status = 'processing'
                order.paid_at = timezone.now()
                order.ref_id = response.get('RefID')
                order.save()
                for item in order.order_items.select_related('product'):
                    Product.objects.filter(id=item.product_id).update(
                        sales_count=F('sales_count') + item.number)
                    ProductColor.objects.filter(
                        product_id=item.product_id, color__name=item.color
                    ).update(number=F('number') - item.number)
                Cart(request).delete_all()
                return render(request, 'cart/payment_result.html',
                              {'success': True, 'order': order, 'message': 'پرداخت با موفقیت انجام شد',
                               'ref_id': order.ref_id})
            else:
                return render(request, 'cart/payment_result.html',
                              {'success': True, 'order': order, 'message': 'پرداخت با موفقیت انجام شد',
                               'ref_id': order.ref_id})
        else:
            if response.get("status") == "ok":
                return render(request, 'cart/payment_result.html', {
                    'message': f'Error code: {response.get("error_code")}, Error Message: {response.get("message")}',
                    'success': False, })
            elif response.get("status") == "cancel":
                return render(request, 'cart/payment_result.html', {
                    'message': f'تراکنش ناموفق بوده است یا توسط کاربر لغو شده است'
                               f'Error Message: {response.get("message")}',
                    'success': False
                })


class DeleteItemOrderView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order_item = get_object_or_404(OrderItem, id=pk, order__user=request.user)
        order = order_item.order
        if order.code_discount > 0:
            order.total_price += order.code_discount
            order.code_discount = 0
        order.total_price -= order_item.price * order_item.number
        order.total_discount -= order_item.discount * order_item.number
        if order.discount_code:
            if order.discount_code.is_valid():
                discount_amount = int(order.total_price * order.discount_code.discount / 100)
                order.code_discount = discount_amount
                order.total_price -= order.code_discount
            else:
                order.discount_code = None

        order_item.delete()
        order.save()
        if order.order_items.count() == 0:
            messages.warning(request, 'سفارش شما خالی شده پس به سبدخرید انتقال مییابد')
            return redirect('cart:cart_detail')
        messages.success(request, 'محصول با موفقیت حذف شد ')
        return redirect('cart:order_detail', order.id)
