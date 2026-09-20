from django.db import models
from accounts.models import User, Address
from products.models import Product
from django_jalali.db import models as jmodels


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    total_price = models.PositiveIntegerField(default=0, verbose_name='جمع قیمت')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'

    def __str__(self):
        return f'{self.user} - {self.created_at} - {"پرداخت شده" if self.is_paid else "پرداخت نشده"}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='محصول')
    size = models.CharField(max_length=10, blank=True, null=True, verbose_name='اندازه')
    color = models.CharField(max_length=255, verbose_name='رنگ')
    warranty = models.CharField(max_length=255, verbose_name='گارانتی')
    number = models.PositiveSmallIntegerField(default=1, verbose_name='تعداد')
    price = models.PositiveIntegerField(verbose_name='قیمت')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f'{self.product} × {self.number}'
