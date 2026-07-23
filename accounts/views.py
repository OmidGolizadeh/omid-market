from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from jdatetime import timedelta
from .forms import LoginForm, RegisterForm, CheckOtpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from accounts.models import User, Otp
from django.core.mail import send_mail
from omid_market import settings
from random import randint
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


def UserLogout(request):
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

