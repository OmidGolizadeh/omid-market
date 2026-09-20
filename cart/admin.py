from django.contrib import admin
from .models import Order, OrderItem


# Register your models here.
class OrderItem_show(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class Order_show(admin.ModelAdmin):
    list_display = ['user', 'total_price', 'created_at', 'is_paid']
    ordering = ['created_at']
    list_filter = ['is_paid', 'created_at']
    inlines = (OrderItem_show,)
