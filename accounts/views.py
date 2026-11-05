from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, View, TemplateView, DetailView, UpdateView
from .forms import LoginForm, RegisterForm, CheckOtpForm, AddressForm, UpdatePersonalInfoForm, ForgetPasswordForm, \
    ResetPasswordForm
from django.contrib.auth import logout, login
from accounts.models import User, Otp, Address, City
from django.core.mail import send_mail
from django.http import JsonResponse
from omid_market import settings
from random import randint
from cart.models import Order
from products.models import Product
from django.db.models import Q
from .utils import send_otp_sms
import jdatetime
import uuid


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    next_page = reverse_lazy('home:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num1 = randint(1, 9)
        num2 = randint(1, 9)
        self.request.session['captcha_answer'] = num1 + num2
        context['captcha_question'] = f"{num1} + {num2}"
        return context

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
        if cd.get('email'):
            send_mail(
                subject='کد تأیید ثبت‌نام',
                message=f'کد تأیید شما: {randcode}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cd['email']],
                fail_silently=False,
            )
        elif cd.get('phone_number'):
            is_sent = send_otp_sms(cd['phone_number'], randcode)
            if not is_sent:
                messages.warning(self.request, 'یگ مشکلی از سامانه پیش آمد')
        print(randcode)
        token = uuid.uuid4()
        Otp.objects.create(username=cd['username'], email=cd.get('email'), phone_number=cd.get('phone_number'),
                           password=cd['password1'], code=randcode, token=token)

        return redirect(reverse('accounts:otp') + f'?token={token}')


class Check_Otp(FormView):
    template_name = 'accounts/check_otp.html'
    form_class = CheckOtpForm
    success_url = reverse_lazy('home:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.GET.get('token')
        remaining = 120

        if token:
            try:
                otp = Otp.objects.get(token=token)
                exp_naive = otp.expiration_date.replace(tzinfo=None)
                now_naive = jdatetime.datetime.now().replace(tzinfo=None)

                elapsed = (now_naive - exp_naive).total_seconds()
                remaining = max(int(120 - elapsed), 0)
            except Otp.DoesNotExist:
                remaining = 0

        context['remaining_time'] = remaining
        return context

    def form_valid(self, form):
        token = self.request.GET.get('token')
        cd = form.cleaned_data

        try:
            otp = Otp.objects.get(code=cd['code'], token=token)
        except Otp.DoesNotExist:
            form.add_error('code', 'کد وارد شده صحیح نیست.')
            return self.form_invalid(form)

        exp_naive = otp.expiration_date.replace(tzinfo=None)
        now_naive = jdatetime.datetime.now().replace(tzinfo=None)
        elapsed = (now_naive - exp_naive).total_seconds()

        if elapsed > 120:
            otp.delete()
            form.add_error('code', 'اعتبار کد به پایان رسیده است.')
            return self.form_invalid(form)

        user = User.objects.create_user(
            username=otp.username,
            email=otp.email,
            password=otp.password,
            phone_number=otp.phone_number,

        )

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
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
    def post(self, request, id):
        address = get_object_or_404(Address, id=id, user=request.user)
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
        context['orders'] = user_order.filter(selected_q).prefetch_related(
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


class ForgetPasswordView(FormView):
    template_name = 'accounts/forget_password.html'
    form_class = ForgetPasswordForm

    def form_valid(self, form):
        identity = form.cleaned_data['identity']
        user = User.objects.get(Q(email=identity) | Q(phone_number=identity))
        randcode = randint(1000, 9999)
        token = uuid.uuid4()
        print(randcode)
        if user.phone_number:
            is_sent = send_otp_sms(user.phone_number, randcode)
            if not is_sent:
                messages.warning(self.request, 'مشکلی در سامانه پیامکی پیش آمد.')
            else:
                masked_phone = f"{user.phone_number[:4]}***{user.phone_number[-4:]}"
                messages.success(self.request, f'کد تایید به شماره موبایل شما ({masked_phone}) ارسال شد.')

        elif user.email:
            send_mail(
                subject='کد تایید تغییر رمز عبور',
                message=f'کد تایید شما: {randcode}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        else:
            form.add_error('identity', 'برای این حساب کاربری هیچ ایمیل یا شماره موبایلی ثبت نشده است.')
            return self.form_invalid(form)
        Otp.objects.create(username=user.username, code=randcode, token=token)
        return redirect(reverse('accounts:reset_password') + f'?token={token}')


class ResetPasswordView(FormView):
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.GET.get('token')
        remaining = 120
        if token:
            try:
                otp = Otp.objects.get(token=token)
                exp_naive = otp.expiration_date.replace(tzinfo=None)
                now_naive = jdatetime.datetime.now().replace(tzinfo=None)
                elapsed = (now_naive - exp_naive).total_seconds()
                remaining = max(int(120 - elapsed), 0)
            except Otp.DoesNotExist:
                remaining = 0

        context['remaining_time'] = remaining
        return context

    def form_valid(self, form):
        token = self.request.GET.get('token')
        cd = form.cleaned_data

        try:
            otp = Otp.objects.get(code=cd['code'], token=token)
        except Otp.DoesNotExist:
            form.add_error('code', 'کد وارد شده صحیح نیست.')
            return self.form_invalid(form)

        exp_naive = otp.expiration_date.replace(tzinfo=None)
        now_naive = jdatetime.datetime.now().replace(tzinfo=None)
        elapsed = (now_naive - exp_naive).total_seconds()

        if elapsed > 120:
            otp.delete()
            form.add_error('code', 'اعتبار کد به پایان رسیده است.')
            return self.form_invalid(form)

        user = User.objects.get(username=otp.username)
        user.set_password(cd['password1'])
        user.save()

        otp.delete()
        messages.success(self.request, 'رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید.')
        return super().form_valid(form)
