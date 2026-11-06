from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('blog', views.BlogView.as_view(), name='blog'),
    path('blog/<str:slug>', views.BlogDetailView.as_view(), name='blog_detail'),
]
