from django.db import models
from django.utils.text import slugify


# Create your models here.

class Product(models.Model):
    Product_Warranty = [
        ('1_month_old', '1 ماهه'),
        ('6_month_old', '6 ماهه'),
        ('12_month_old', '12 ماهه'),
    ]
    title = models.CharField(max_length=255, verbose_name='نام محصول')
    description = models.TextField(blank=True, null=True, verbose_name='توضیح')
    short_description = models.TextField(blank=True, null=True, verbose_name='نوضیح کوتاه')
    price = models.DecimalField(max_digits=11, blank=True, null=True, decimal_places=0, verbose_name='قیمت')
    discount = models.DecimalField(max_digits=11, blank=True, null=True, decimal_places=0, verbose_name='تخفیف')
    number = models.IntegerField(blank=True, null=True, verbose_name='تعداد')
    warranty = models.CharField(null=True, blank=True, choices=Product_Warranty, verbose_name='گارانتی')
    slug = models.SlugField(verbose_name='اسلاگ')
    images = models.ImageField(null=True, blank=True, verbose_name='تصویر')
    score = models.FloatField(default=0.0, null=True, blank=True, verbose_name='امتیاز')

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

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    name_color = models.CharField(max_length=255, blank=True, null=True, verbose_name='رنگ')
    color_code = models.CharField(max_length=7, help_text="مثال: #FF5733", verbose_name='کد رنگ')

    class Meta:
        verbose_name = 'رنگ محصول'
        verbose_name_plural = 'رنگ محصول ها'

    def __str__(self):
        return f'{self.product} - {self.name_color}'


class Product_Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    images = models.ImageField(null=True, blank=True, verbose_name='تصویر')

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصویر محصول ها'

    def __str__(self):
        return self.product


class Category_brnd(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    title = models.CharField(max_length=255, verbose_name='نام برند')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'برند محصول'
        verbose_name_plural = 'برند محصول ها'

    def __str__(self):
        return self.title


class Category(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    title = models.CharField(max_length=255, verbose_name='نوع محصول')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'نوع محصول'
        verbose_name_plural = 'نوع محصول ها'

    def __str__(self):
        return self.title
