from django.db import models
from django_jalali.db import models as jmodels


# Create your models here.

class About_the_store(models.Model):
    description = models.TextField(null=True, blank=True, verbose_name='توضیح')
    short_description = models.TextField(null=True, blank=True, verbose_name='توضیح کوتاه')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره تلفن')
    map_address = models.URLField(blank=True, null=True, verbose_name='آدرس نقشه')
    address = models.CharField(max_length=20, null=True, blank=True, verbose_name='آدرس')
    email = models.CharField(null=True, blank=True, verbose_name='ایمیل')

    def __str__(self):
        return self.short_description[:30]

    class Meta:
        verbose_name = 'اطلاعات درباره فروشگاه'
        verbose_name_plural = 'اطلاعات های درباره فروشگاه'


class Contact_us(models.Model):
    name = models.CharField(max_length=20, verbose_name='نام')
    phone = models.CharField(max_length=11, verbose_name='شماره تلفن')
    email = models.EmailField(verbose_name='ایمیل')
    title = models.CharField(max_length=15, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    created_at = jmodels.jDateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='زمان دریافت پیام')

    def __str__(self):
        return f'{self.name} -  {self.title}'

    class Meta:
        verbose_name = 'ارتباط با ما'
        verbose_name_plural = 'ارتباط ها با ما'


class Team(models.Model):
    full_name = models.CharField(max_length=30, verbose_name='نام کامل')
    expertise = models.CharField(max_length=30, verbose_name='تخصص')
    position = models.CharField(max_length=50, verbose_name='مقام')
    image = models.ImageField(upload_to='images/teams', null=True, blank=True, verbose_name='تصویر')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'نیم'
        verbose_name_plural = 'تیم ها'


class Link(models.Model):
    Link_title = {
        ('FACEBOOK', 'فیس‌بوک'), ('LINKEDIN', 'لینکدین'), ('X', 'ایکس'),
        ('YOUTUBE', 'یوتیوب'), ('INSTA', 'اینستا'), ('TELEGRAM', 'تلگرام'),
    }
    title = models.CharField(max_length=25, choices=Link_title, verbose_name='عنوان')
    url = models.URLField(blank=True, null=True, verbose_name='لینک شبکه های اجتمایی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'لینک شبکه اجتمایی'
        verbose_name_plural = 'لینک شبکه های اجتمایی'


class BannerLink(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='موضوغ')
    image = models.ImageField(upload_to='images/banners', null=True, blank=True, verbose_name='بنر')
    url = models.CharField(max_length=500, blank=True, null=True, verbose_name='آدرس')
    main_banner = models.BooleanField(default=False, blank=True, null=True, verbose_name='بتر اصلی')
    second_banner = models.BooleanField(default=False, blank=True, null=True, verbose_name='بنر فرعی')
    second_url = models.BooleanField(default=False, blank=True, null=True, verbose_name='آدرس فرعی')
    order = models.PositiveSmallIntegerField(default=0, blank=True, null=True, verbose_name='ترتیب')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریج ایجاد')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'بنر و لینک نخست'
        verbose_name_plural = '	بنرها و لینک‌های نخست'

    def __str__(self):
        return f'{self.title}-{self.url}-{self.order}'
