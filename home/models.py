from django.db import models


# Create your models here.

class About_the_store(models.Model):
    description = models.TextField(null=True, blank=True, verbose_name='توضیح')
    short_description = models.TextField(null=True, blank=True, verbose_name='توضیح کوتاه')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره تلفن')
    map_address = models.URLField(blank=True, null=True, verbose_name='آدرس نقشه')

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
    Message = models.TextField(verbose_name='پیام')

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
    title = models.CharField(max_length=25, verbose_name='عنوان')
    url = models.URLField(blank=True, null=True, verbose_name='لینک شبکه های اجتمایی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'لینک شبکه اجتمایی'
        verbose_name_plural = 'لینک شبکه های اجتمایی'
