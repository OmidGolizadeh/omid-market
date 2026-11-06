from django.db import models
from accounts.models import User
from django.utils.text import slugify
from django_jalali.db import models as jmodels


class Category(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='دسته بندی')
    slug = models.SlugField(unique=True, allow_unicode=True, null=True, blank=True, verbose_name='اسلاگ')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'دسته بندی بلاگ'
        verbose_name_plural = 'دسته بندی های بلاگ'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Label_Article(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='نام')
    slug = models.SlugField(unique=True, allow_unicode=True, null=True, blank=True, verbose_name='اسلاک')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name='نویسنده')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='articles',
                                 verbose_name='دسته بندی')
    label = models.ManyToManyField(Label_Article, related_name='articles', verbose_name='برچسب ها ')
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='موضوع')
    short_description = models.TextField(blank=True, null=True, verbose_name='نوضیح کوتاه')
    body = models.TextField(blank=True, null=True, verbose_name='توضیخات')
    views = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید ها')
    image = models.ImageField(upload_to='blog', blank=True, null=True, verbose_name='تصویر')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True,
                            verbose_name='اسلاگ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'وبلاگ'
        verbose_name_plural = 'وبلاگ ها '
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or 'article'
            slug, n = base, 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super(Article, self).save(*args, **kwargs)


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='وبلاگ')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='کاربر')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                               verbose_name='منبع')
    body = models.TextField(blank=True, null=True, verbose_name='پیام')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.article}-{self.user}-{self.parent}'
