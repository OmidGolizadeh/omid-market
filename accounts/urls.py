from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register', views.Register.as_view(), name='register'),
    path('logout/', views.UserLogout, name='logout'),
    path('otp/', views.Check_Otp.as_view(), name='otp'),
]
