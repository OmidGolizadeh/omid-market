from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

"""
path('profile/address',cache_page(60 * 1)(views.LoadCityView.as_view()) , name='profile_address'),
این نوع cache کردن است 
cache_page(60 * 1) = 1 دقیقه cache رو انجام میده 
"""

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register', views.Register.as_view(), name='register'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('otp/', views.Check_Otp.as_view(), name='otp'),
    path('profile/address', views.AddressView.as_view(), name='profile_address'),
    path('profile/address/load-cities', views.LoadCityView.as_view(), name='profile_address_city'),
    path('profile/address_delete/<int:id>', views.AddressDelete.as_view(), name='profile_address_delete'),
    path('profile/personal-info', views.ProfileView.as_view(), name='personal-info'),
    path('profile/favorites', views.FavoritesView.as_view(), name='favorites'),
    path('profile/factors', views.FactorsView.as_view(), name='factors'),
    path('invoice/<int:pk>/', views.InvoiceView.as_view(), name='invoice'),
    path('profile/edit/', views.UpdatePersonalInfoView.as_view(), name='profile_edit'),
    path('forget-password/', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
]
