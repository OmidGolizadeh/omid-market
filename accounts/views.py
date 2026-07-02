from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from accounts.models import User


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
    return redirect('home:home')


class Register(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
        )
        return super().form_valid(form)
