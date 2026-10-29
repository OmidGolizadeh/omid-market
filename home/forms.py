from django import forms
from .models import Contact_us, BannerLink
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html, format_html_join
from products.models import Product, Category, Category_brand


class Contact_Form(forms.ModelForm):
    class Meta:
        model = Contact_us
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'name': 'name',
                'id': 'name',
                'placeholder': 'نام خود وارد کنید',
                'required': '',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'name': 'tel',
                'id': 'tel',
                'placeholder': 'شماره تلفن خود وارد کنید',
                'required': '',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'name': 'email',
                'id': 'email',
                'placeholder': 'ایمیل خود وارد کنید ',
                'style': 'text-align: right; direction: rtl;',
                'required': '',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'name': 'subject',
                'id': 'subject',
                'placeholder': 'موضوع خود وارد کنید',
                'required': '',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'name': 'message',
                'id': 'message',
                'placeholder': 'پیام خود را وارد کنید',
                'required': '',
                'rows': '3'
            })
        }


def get_url_suggestions():
    items = []
    for name, label in [
        ('home:home', 'صفحه نخست'),
        ('home:about', 'درباره ما'),
        ('home:contact', 'تماس با ما'),
        ('home:faq', 'سوالات متداول'),
        ('products:product', 'همه محصولات (کاشی)'),
        ('products:product_list', 'همه محصولات (لیست)'),
    ]:
        try:
            items.append((reverse(name), label))
        except NoReverseMatch:
            pass

    shop = reverse('products:product')
    items += [
        (f'{shop}?sort=newest', 'فیلتر: جدیدترین'),
        (f'{shop}?sort=views', 'فیلتر: پربازدیدترین'),
        (f'{shop}?sort=cheapest', 'فیلتر: ارزان‌ترین'),
        (f'{shop}?only_available=1', 'فیلتر: فقط کالاهای موجود'),
        (f'{shop}?only_warranty=1', 'فیلتر: فقط دارای گارانتی'),
    ]

    for c in Category.objects.exclude(slug__isnull=True).exclude(slug=''):
        items.append((f'{shop}?category={c.slug}', f'دسته‌بندی: {c.title}'))
    for b in Category_brand.objects.exclude(title=''):
        items.append((f'{shop}?brand={b.title}', f'{shop}?brand={b.id}'))
    for p in Product.objects.exclude(slug='').only('title', 'slug'):
        items.append((reverse('products:product_detail', args=[p.slug]), f'محصول: {p.title}'))
    return items


class DatalistInput(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        list_id = f'{name}_datalist'
        attrs['list'] = list_id
        attrs['style'] = 'width: 600px;'
        attrs['autocomplete'] = 'off'
        input_html = super().render(name, value, attrs, renderer)
        options = format_html_join(
            '', '<option value="{}">{}</option>', get_url_suggestions()
        )
        return format_html('{}<datalist id="{}">{}</datalist>', input_html, list_id, options)


class BannerLinkForm(forms.ModelForm):
    url = forms.CharField(
        required=False,
        max_length=200,
        label='آدرس',
        widget=DatalistInput(),
    )

    class Meta:
        model = BannerLink
        fields = '__all__'
