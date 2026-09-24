from django.db import models
from django.utils.text import slugify
from django_jalali.db import models as jmodels
from django.db.models import Sum
from accounts.models import User
from django.utils import timezone


class Category_brand(models.Model):
    title = models.CharField(max_length=255, verbose_name='نام برند')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'برند محصول'
        verbose_name_plural = 'برند محصول ها'

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='نوع محصول')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نوع محصول'
        verbose_name_plural = 'نوع محصول ها'

    def __str__(self):
        return self.title


class Warranty(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='نام کارانتی')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'کارانتی'
        verbose_name_plural = 'کارانتی ها'

    def __str__(self):
        return self.title


class Product(models.Model):
    Product_Warranty = [
        ('not_warranty', 'بدون گارانتی'),
        ('1_month_old', '1 ماهه'),
        ('6_month_old', '6 ماهه'),
        ('12_month_old', '12 ماهه'),
    ]
    title = models.CharField(max_length=255, verbose_name='نام محصول')
    description = models.TextField(blank=True, null=True, verbose_name='توضیح')
    short_description = models.TextField(blank=True, null=True, verbose_name='نوضیح کوتاه')
    price = models.DecimalField(max_digits=11, blank=True, null=True, decimal_places=0, verbose_name='قیمت')
    discount_percent = models.PositiveSmallIntegerField(default=0, blank=True, null=True, verbose_name='درصد تخفیف',
                                                        help_text='مثلاً ۱۵ یعنی ۱۵ درصد تخفیف')
    discount_expire = jmodels.jDateTimeField(null=True, blank=True, verbose_name='تاریخ پایان تخفیف',
                                             help_text='بعد از این تاریخ تخفیف اعمال نمی‌شود'
                                             )
    brand = models.ForeignKey(Category_brand, on_delete=models.CASCADE, null=True, verbose_name='برند ')
    Category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name='توع محصول')
    warranty = models.ManyToManyField(Warranty, blank=True, verbose_name='گارانتی')
    slug = models.SlugField(unique=True, blank=True, verbose_name='اسلاگ')
    images = models.ImageField(upload_to='products/%Y/%m/%d/', null=True, blank=True, verbose_name='تصویر')
    score = models.FloatField(default=0.0, null=True, blank=True, verbose_name='امتیاز')
    view = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    created_at = jmodels.jDateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='تاریخ ایجاد محصول')

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصول ها'

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.slug = slugify(self.title)
        super(Product, self).save(*args)

    @property
    def is_discount_active(self):
        if not self.discount_percent or self.discount_percent <= 0:
            return False
        if self.discount_expire:
            now = timezone.now()
            expire = self.discount_expire
            if hasattr(expire, 'togregorian'):
                expire = expire.togregorian()
            if now > expire:
                return False
        return True

    @property
    def total_stock(self):
        try:
            result = self.color.aggregate(total=Sum('number'))['total']
            return result or 0
        except Exception:
            return 0

    @property
    def final_price(self):
        """قیمت بعد از اعمال تخفیف"""
        if self.is_discount_active and self.price:
            return int(self.price * (100 - self.discount_percent) / 100)
        return int(self.price) if self.price else 0

    @property
    def discount_amount(self):
        """مبلغ تخفیف به تومان"""
        if self.is_discount_active and self.price:
            return int(self.price) - self.final_price
        return 0

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color', verbose_name='محصول')
    name_color = models.CharField(max_length=255, blank=True, null=True, verbose_name='رنگ')
    color_code = models.CharField(max_length=7, help_text="مثال: #FF5733", verbose_name='کد رنگ')
    number = models.IntegerField(blank=True, null=True, verbose_name='تعداد')
    created_at = jmodels.jDateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'رنگ محصول'
        verbose_name_plural = 'رنگ محصول ها'

    def __str__(self):
        return f'{self.product} - {self.name_color}'


class Product_Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_Image', verbose_name='محصول')
    images = models.ImageField(null=True, blank=True, verbose_name='تصویر')
    created_at = jmodels.jDateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصویر محصول ها'

    def __str__(self):
        return self.product.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment', verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comment', verbose_name='محصول')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies',
                               verbose_name='منبع')
    body = models.TextField(verbose_name='پیام ارسال شده')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'

    def __str__(self):
        return f'{self.user} - {self.product}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes', verbose_name='محصول')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'لایک'
        verbose_name_plural = 'لایک ها'

        constraints = [
            models.UniqueConstraint(fields=['user', 'product'],
                                    name='unique_user_product_like')
        ]

    def __str__(self):
        return f'{self.user} - {self.product}'
