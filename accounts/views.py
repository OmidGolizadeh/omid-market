from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, View, TemplateView, DetailView, UpdateView
from jdatetime import timedelta
from .forms import LoginForm, RegisterForm, CheckOtpForm, AddressForm, UpdatePersonalInfoForm
from django.contrib.auth import logout, login
from accounts.models import User, Otp, Address, City
from django.core.mail import send_mail
from django.http import JsonResponse
from omid_market import settings
from random import randint
from cart.models import Order
from products.models import Product
from django.db.models import Q
import uuid


# Create your views here.

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    next_page = reverse_lazy('home:home')

    def form_valid(self, form):
        # user = form.get_user()
        messages.success(self.request, 'کاربر وارد شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'یک مشکل به وجود امد دوباره تلاش کنید')
        return super().form_invalid(form)


class UserLogout(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.error(request, 'کاربر خارج شد.')
        return redirect('home:home')


class Register(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:otp')

    def form_valid(self, form):
        cd = form.cleaned_data
        randcode = randint(1000, 9999)
        send_mail(
            subject='کد تأیید ثبت‌نام',
            message=f'کد تأیید شما: {randcode}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cd['email']],
            fail_silently=False,
        )
        print(randcode)
        token = uuid.uuid4()
        Otp.objects.create(username=cd['username'], email=cd['email'], password=cd['password1'], code=randcode,
                           token=token)

        return redirect(reverse('accounts:otp') + f'?token={token}')


class Check_Otp(FormView):
    template_name = 'accounts/check_otp.html'
    form_class = CheckOtpForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        token = self.request.GET.get('token')
        cd = form.cleaned_data

        try:
            otp = Otp.objects.get(code=cd['code'], token=token)
        except Otp.DoesNotExist:
            form.add_error('code', 'کد وارد شده صحیح نیست.')
            return self.form_invalid(form)

        if timezone.now() - otp.expiration_date > timedelta(minutes=2):
            otp.delete()
            form.add_error('code', 'اعتبار کد به پایان رسیده است.')
            return self.form_invalid(form)

        user = User.objects.create_user(
            username=otp.username,
            email=otp.email,
            password=otp.password
        )

        login(self.request, user)
        otp.delete()

        return super().form_valid(form)


class AddressView(LoginRequiredMixin, FormView):
    template_name = 'accounts/address.html'
    form_class = AddressForm
    success_url = reverse_lazy('accounts:profile_address')

    def form_valid(self, form):
        address_count = Address.objects.filter(user=self.request.user).count()
        if address_count >= 5:
            messages.error(self.request, 'شما نمی‌توانید بیش از ۵ آدرس ذخیره کنید.')
            return super().form_valid(form)
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        messages.success(self.request, 'آدرس با موفقیت ثبت شد.')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user).select_related('province',
                                                                                             'city').order_by(
            '-created_at')
        return context


class LoadCityView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        province_id = request.GET.get('province')
        if not province_id:
            return JsonResponse([], safe=False)

        cities = City.objects.filter(province_id=province_id).order_by('name')
        data = [{'id': city.id, 'name': city.name} for city in cities]
        return JsonResponse(data, safe=False)


class AddressDelete(LoginRequiredMixin, View):
    def get(self, request, id):
        address = Address.objects.get(id=id)
        if address:
            address.delete()
        return redirect('accounts:profile_address')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/personal-info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = (Order.objects.filter(user=self.request.user, is_paid=True).order_by('-created_at').first())
        return context


class FavoritesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = Product.objects.filter(likes__user=self.request.user).order_by('-created_at')
        return context


STATUS_TABS = [
    ('pending', 'در انتظار پرداخت', Q(is_paid=False)),
    ('paid', 'پرداخت شده', Q(is_paid=True, status='processing')),
    ('shipped', 'ارسال شده', Q(is_paid=True, status='shipped')),
    ('completed', 'تکمیل شده', Q(is_paid=True, status='completed')),
]


class FactorsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/factors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_order = Order.objects.filter(user=self.request.user)
        key = [t[0] for t in STATUS_TABS]
        current = self.request.GET.get('status')
        if current not in key:
            current = 'pending'
        tabs = []
        selected_q = None
        for key, title, cond in STATUS_TABS:
            tabs.append({'key': key, 'title': title, 'cond': user_order.filter(cond).count(), 'active': key == current})
            if key == current:
                selected_q = cond
        context['tabs'] = tabs
        context['current'] = current
        context['orders'] = Order.objects.filter(selected_q).prefetch_related(
            'order_items__product').order_by('-created_at')
        return context


class InvoiceView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/invoice.html'
    context_object_name = 'order'

    def get_queryset(self):
        return (Order.objects.filter(user=self.request.user, is_paid=True)
        .select_related('user', 'address', 'address__province', 'address__city').prefetch_related(
            'order_items__product'))


class UpdatePersonalInfoView(LoginRequiredMixin, UpdateView):
    form_class = UpdatePersonalInfoForm
    template_name = 'accounts/personal-info-edit.html'
    success_url = reverse_lazy('accounts:personal-info')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'اطلاعات با موفقیت ذخیره شد.')
        return super().form_valid(form)
