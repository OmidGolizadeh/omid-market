from django.contrib import admin
from . import models as product_model
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea, TextInput


class ProductSpecificationInline(admin.TabularInline):
    model = product_model.ProductSpecification
    extra = 3



@admin.register(product_model.SpecificationGroup)
class SpecificationGroup_show(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_filter = ['order']
    search_fields = ['title']
    ordering = ['order']


@admin.register(product_model.Overall_Color)
class ProductColor_show(admin.ModelAdmin):
    list_display = ['name', 'show_color', ]
    readonly_fields = ('created_at',)
    ordering = ['created_at']

    def show_color(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: #{}; border-radius: 50%; border: 1px solid #ccc;"></div>',
                obj.color_code
            )
        return "بدون رنگ"

    show_color.short_description = 'نمایش رنگ'


class Rating_show(admin.TabularInline):
    model = product_model.Rating
    extra = 1
    fields = ['user', 'product', 'comment', 'score', 'created_at']
    readonly_fields = ('user', 'product', 'comment', 'score', 'created_at',)
    ordering = ('created_at',)


@admin.register(product_model.Rating)
class Rating_show_score(admin.ModelAdmin):
    list_display = ['user', 'product', 'comment', 'score', 'created_at']
    list_filter = ['product', 'score']
    search_fields = ['user', 'product', 'score']
    readonly_fields = ('user', 'product', 'comment', 'score', 'created_at',)
    ordering = ('created_at',)


class Product_Image_show(admin.TabularInline):
    model = product_model.Product_Image
    extra = 1
    fields = ('images', 'show_image_product', 'created_at')
    readonly_fields = ('show_image_product', 'created_at')
    ordering = ['created_at']

    def show_image_product(self, obj):
        if obj.pk and obj.images:
            return format_html(
                '<img src="{}" width="90" height="90" style="object-fit:cover; border-radius:8px;" />',
                obj.images.url
            )
        return "بدون تصویر"

    show_image_product.short_description = "پیش‌نمایش"


@admin.register(product_model.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'id', 'user', 'body_short', 'parent', 'created_at']
    list_filter = ['created_at', 'product']
    search_fields = ['body', 'user__username', 'user__full_name', 'product__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_select_related = ['product', 'user', 'parent']
    autocomplete_fields = ['product']  # نیاز به search_fields در ProductAdmin دارد
    list_per_page = 20

    @admin.display(description='متن کامنت')
    def body_short(self, obj):
        body = obj.body or ''
        return body[:50] + '...' if len(body) > 50 else body

    def get_readonly_fields(self, request, obj=None):
        # user فقط روی کامنت‌های موجود readonly باشد
        if obj:
            return ['user', 'created_at']
        return ['created_at']

    def get_exclude(self, request, obj=None):
        # هنگام افزودن، user خودکار پر می‌شود و در فرم نمایش داده نمی‌شود
        return None if obj else ['user']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            object_id = request.resolver_match.kwargs.get('object_id')
            if object_id:
                comment = product_model.Comment.objects.filter(pk=object_id).first()
                if comment:
                    kwargs['queryset'] = product_model.Comment.objects.filter(
                        product_id=comment.product_id
                    ).exclude(pk=comment.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class Like_show(admin.TabularInline):
    model = product_model.Like
    extra = 0
    fields = ('user', 'created_at')
    readonly_fields = ('user', 'created_at')
    ordering = ['-created_at']
    can_delete = False


@admin.register(product_model.Product)
class Product_show(admin.ModelAdmin):
    list_display = (
        'title', 'short_description_truncated', 'price', 'show_image_product', 'get_total_stock', 'view', 'sales_count',
        'likes_count', 'comments_count')
    readonly_fields = ('created_at',)
    search_fields = ['title', 'short_description_truncated', ]
    ordering = ['title', '-created_at']
    list_filter = ['created_at']
    inlines = (Product_Image_show, Like_show, Rating_show, ProductSpecificationInline)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, product_model.Comment) and not instance.user_id:
                instance.user = request.user
            instance.save()
        formset.save_m2m()

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

    def likes_count(self, obj):
        count = obj.likes.count()
        if count > 0:
            return format_html(
                '<span style="background:#FFC107; color:white; padding:3px 8px; border-radius:12px; font-size:12px;">❤️ {}</span>',
                count
            )
        return format_html('<span style="color:#94a3b8;">۰ لایک</span>')

    def comments_count(self, obj):
        count = obj.comment.count()
        if count > 0:
            return format_html(
                '<span style="background:#3b82f6; color:white; padding:3px 8px; border-radius:12px; font-size:12px;">💬 {}</span>',
                count
            )
        return format_html('<span style="color:#94a3b8;">۰ کامنت</span>')

    show_image_product.short_description = "تصویر"
    short_description_truncated.short_description = 'توضیحات (خلاصه)'
    get_total_stock.short_description = 'تعداد کل'
    likes_count.short_description = 'لایک ها'
    comments_count.short_description = 'کامت ها'


@admin.register(product_model.Category)
class Category_show(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created_at']
    readonly_fields = ('created_at',)
    search_fields = ('title', 'slug')
    ordering = ['title', 'created_at']
    filter_horizontal = ('categories',)


@admin.register(product_model.Category_brand)
class Category_brand_show(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('created_at',)
    ordering = ['title', 'created_at']


@admin.register(product_model.ProductColor)
class ProductColor_show(admin.ModelAdmin):
    list_display = ['product', 'show_color', 'number']
    readonly_fields = ('created_at',)
    ordering = ['product', 'created_at']

    def show_color(self, obj):
        if obj.color.color_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: #{}; border-radius: 50%; border: 1px solid #ccc;"></div>',
                obj.color.color_code
            )
        return "بدون رنگ"

    show_color.short_description = 'نمایش رنگ'


@admin.register(product_model.Warranty)
class Warranty_show(admin.ModelAdmin):
    list_display = ['title']
