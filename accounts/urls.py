from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register', views.Register.as_view(), name='register'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('otp/', views.Check_Otp.as_view(), name='otp'),
    path('profile/address', views.AddressView.as_view(), name='profile_address'),
    path('profile/address/load-cities', views.LoadCityView.as_view(), name='profile_address_city'),
    path('profile/address_delete/<int:id>', views.AddressDelete.as_view(), name='profile_address_delete'),
]
