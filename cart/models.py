from django.db import models
from accounts.models import User, Address
from products.models import Product
from django_jalali.db import models as jmodels
from django.utils import timezone
from datetime import timedelta


class DiscountCode(models.Model):
    name = models.CharField(max_length=10, verbose_name='نام')
    discount = models.SmallIntegerField(default=0, verbose_name='درصد تخفیف')
    number = models.SmallIntegerField(default=1, verbose_name='تغداد')
    expire_date = jmodels.jDateTimeField(null=True, blank=True, verbose_name='تاریخ انقضا',
                                         help_text='بعد از این تاریخ کد دیگر معتبر نیست'
                                         )
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کد تخفیف ها'

    def is_valid(self):
        if self.number <= 0:
            return False
        if self.expire_date:
            now = timezone.now()
            expire = self.expire_date
            if hasattr(expire, 'togregorian'):
                expire = expire.togregorian()
            if now > expire:
                return False
        return True

    def save(self, *args, **kwargs):
        if hasattr(self, 'day') and self.day and not self.expire_date:
            self.expire_date = timezone.now() + timedelta(days=self.day)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}-{self.discount}-{self.number}'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    total_price = models.PositiveIntegerField(default=0, verbose_name='جمع قیمت')
    total_discount = models.PositiveIntegerField(default=0, verbose_name='جمع تخفیف')
    code_discount = models.PositiveIntegerField(default=0, verbose_name='تخفیف کد تخفیف')
    discount_code = models.ForeignKey('DiscountCode', null=True, blank=True, on_delete=models.SET_NULL,
                                      verbose_name='کد تخفیف')
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
    discount = models.PositiveIntegerField(default=0, verbose_name='تخفیف واحد')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f'{self.product} × {self.number}'
