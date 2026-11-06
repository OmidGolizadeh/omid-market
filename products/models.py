from django.db import models
from django.utils.text import slugify
from django_jalali.db import models as jmodels
from django.db.models import Sum, Avg
from accounts.models import User
from django.utils import timezone


class SpecificationGroup(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='عنوان گروه')
    order = models.PositiveSmallIntegerField(default=0, blank=True, null=True, verbose_name='ترتیب')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'گروه مشخصات'
        verbose_name_plural = 'گروه های مشخصات'

    def __str__(self):
        return f'{self.title}'


class Overall_Color(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='نام رنگ')
    color_code = models.CharField(max_length=7, help_text="مثال: #FF5733", verbose_name='کد رنگ')
    created_at = jmodels.jDateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'رنگ کلی'
        verbose_name_plural = 'رنگ های کلی'

    def __str__(self):
        return f'{self.name}-{self.color_code}'


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
    categories = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_categories',
                                        verbose_name='دسته‌بندی')
    slug = models.SlugField(unique=True, allow_unicode=True, null=True, blank=True, verbose_name='اسلاگ')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'نوع محصول'
        verbose_name_plural = 'نوع محصول ها'

    def __str__(self):
        return self.title


class Warranty(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='نام کارانتی')
    price = models.DecimalField(max_digits=11, blank=True, null=True, decimal_places=0, verbose_name='قیمت کارانتی')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'کارانتی'
        verbose_name_plural = 'کارانتی ها'

    def __str__(self):
        return f'{self.title}-{self.price}'


class Product(models.Model):
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
    sales_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    created_at = jmodels.jDateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='تاریخ ایجاد محصول')

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصول ها'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.slug, allow_unicode=True) or 'product'
            slug, n = base, 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super(Product, self).save(*args, **kwargs)

    def warranty_price(self):
        total = self.warranty.get('price')
        if total:
            self.price = self.price + total
            return self.price

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

    def update_score(self):
        score_data = self.ratings.aggregate(Avg('score'))
        avg_score = score_data['score__avg']
        if avg_score is not None:
            self.score = round(avg_score, 1)
        else:
            self.score = 0.0
        self.save()

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color', verbose_name='محصول')
    color = models.ForeignKey(Overall_Color, on_delete=models.CASCADE, null=True, blank=True, related_name='color',
                              verbose_name='رنگ')
    number = models.IntegerField(blank=True, null=True, verbose_name='تعداد')
    created_at = jmodels.jDateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'رنگ محصول'
        verbose_name_plural = 'رنگ محصول ها'

    def __str__(self):
        return f'{self.product} - {self.color.name}'


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


class Rating(models.Model):
    Rating_Number = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings', verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings', verbose_name='محصول')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, related_name='ratings',
                                verbose_name='کامنت')
    score = models.IntegerField(choices=Rating_Number, verbose_name='امتیاز')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'امتیاز'
        verbose_name_plural = 'امتیازها'

        constraints = [
            models.UniqueConstraint(fields=['user', 'product'],
                                    name='unique_user_product_rating')
        ]

    def __str__(self):
        return f'{self.user}-{self.product}-{self.comment}-{self.score}'


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='specifications',
                                verbose_name='محصول')
    group = models.ForeignKey(SpecificationGroup, on_delete=models.CASCADE, null=True, blank=True, verbose_name='گروه')
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='عنوان (مثلاً طول)')
    value = models.CharField(max_length=255, null=True, blank=True, verbose_name='مقدار (مثلاً ۳۲ سانتی‌متر)')
    order = models.PositiveSmallIntegerField(default=0, null=True, blank=True, verbose_name='ترتیب')

    class Meta:
        ordering = ['group__order', 'group_id', 'order', 'id']
        verbose_name = 'مشخصه محصول'
        verbose_name_plural = 'مشخصات محصول'

    def __str__(self):
        return f'{self.product}-{self.title}'
