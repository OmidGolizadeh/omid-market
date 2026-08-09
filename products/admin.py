from django.contrib import admin
from .models import Product, Category, Category_brand, ProductColor, Product_Image, Warranty, Comment
from django.utils.html import format_html


@admin.register(Product)
class Product_show(admin.ModelAdmin):
    list_display = (
        'title', 'short_description_truncated', 'price', 'show_image_product', 'get_total_stock', 'view')
    readonly_fields = ('created_at',)
    ordering = ['title', 'created_at']

    def short_description_truncated(self, obj):
        text = obj.short_description
        if text and len(text) > 50:
            return text[:50] + '...'
        return text

    def show_image_product(self, obj):
        if obj.images:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:50%;" />', obj.images.url)
        return "بدون تصویر"

    def get_total_stock(self, obj):
        return obj.total_stock

    show_image_product.short_description = "تصویر"
    short_description_truncated.short_description = 'توضیحات (خلاصه)'
    get_total_stock.short_description = 'تعداد کل'


@admin.register(Category)
class Category_show(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('created_at',)
    ordering = ['title', 'created_at']


@admin.register(Category_brand)
class Category_brand_show(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('created_at',)
    ordering = ['title', 'created_at']


@admin.register(Product_Image)
class Product_Image_show(admin.ModelAdmin):
    list_display = ['product', 'show_image_product']
    readonly_fields = ('created_at',)
    ordering = ['product', 'created_at']

    def show_image_product(self, obj):
        if obj.images:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:50%;" />', obj.images.url)
        return "بدون تصویر"

    show_image_product.short_description = "تصویر"


@admin.register(ProductColor)
class ProductColor_show(admin.ModelAdmin):
    list_display = ['product', 'name_color', 'show_color', 'number']
    readonly_fields = ('created_at',)
    ordering = ['product', 'created_at']

    def show_color(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: #{}; border-radius: 50%; border: 1px solid #ccc;"></div>',
                obj.color_code
            )
        return "بدون رنگ"

    show_color.short_description = 'نمایش رنگ'


@admin.register(Warranty)
class Warranty_show(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Comment)
class Comment_show(admin.ModelAdmin):
    list_display = ['user', 'product', 'parent_show', ]
    ordering = ['user', 'created_at']
    readonly_fields = ('created_at',)
    list_filter = ['created_at']

    def parent_show(self, obj):
        parent = obj.parent
        if not parent:
            return 'هیج منبع وجود ندارد .'
        else:
            return parent

    parent_show.short_description = 'منبع'
